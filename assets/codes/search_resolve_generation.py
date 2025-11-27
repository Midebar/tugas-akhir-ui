def process_example(example, counter):               
    try:
        print(f"Running example: {example['id']}")

        flag = 'true'
        reasoning_step = []
        search_round = 0
        
        normalized_context = example['normalized_context']
        cleaned_normalized_context = self.clean_conjecture(normalized_context)
        normalized_context_list = cleaned_normalized_context.splitlines()
        normalized_context_list = [
            '\n'.join(self.remove_negations(line) for line in item.replace('\\textnormal', '').replace('\\textrm', '').replace('\\\\text', '\\text')
                    .replace('\\text', '').replace('-', '') 
                    .replace('{', '').replace('}', '').replace('\\right', '')
                    .replace('\\left', '').replace('\\newline', '\n').replace('$', '').split('\n'))
            for item in normalized_context_list if "(" in item and ")" in item
        ]
        
        normalized_conjecture = self.clean_conjecture(example['normalized_conjecture'])
        negated_label = example['negated_label']
        sos_list = self.clean_conjecture(example['sos_list'])
        if '(' not in sos_list and ')' not in sos_list:
            sos_list = normalized_conjecture
            sos_list = self.remove_negations(sos_list)
            if example['negated_label'] == 'True':
                sos_list = self.negate_boolean(sos_list)
                
        modified_context_list = []
        for item in normalized_context_list:
            item = next((p.strip() for p in item.split(":::", 1) if "(" in p), "")
            if '\\wedge' in item:
                split_items = item.split('\\wedge')
                modified_context_list.extend([sub_item.strip() for sub_item in split_items])
            elif '\\land' in item:
                split_items = item.split('\\land')
                modified_context_list.extend([sub_item.strip() for sub_item in split_items])
            elif '\u2227' in item:
                split_items = item.split('\u2227')
                modified_context_list.extend([sub_item.strip() for sub_item in split_items]) 
            else:
                modified_context_list.append(item)
        normalized_context_list = [item for item in modified_context_list if "(" in item and ")" in item]
        print("Normalized Context List: ", normalized_context_list)
        print("Normalized Conjecture: ", normalized_conjecture)
        print("sos_list: ", sos_list)
        
        normalized_context_list.append(sos_list)
        
        list_of_sos = []
        list_of_compelment = []
        
        selected_clause = None
            
        while flag == 'true':
            if search_round >= self.search_round:
                final_answer = "No final answer found in the text."
                break
            
            if selected_clause == None:
                print("Search Router Operating...")
                print("Running: ", example['id'])
                print("Ground truth: ", example['ground_truth'])
                
                complement_indices = self.filter_complementary_context(normalized_context_list, sos_list)
                print("Complement Indices: ", complement_indices)
                
                if complement_indices:
                    potential_clauses = [normalized_context_list[index] for index in complement_indices]

                    # Normalize sos_list and reasoning_step entries for robust duplicate checking
                    norm_sos = normalize_clause_for_compare(sos_list)
                    used_pairs = set()
                    for step in reasoning_step:
                        # step is [sos, selected_clause, new_clause]
                        used_sos = normalize_clause_for_compare(step[0])
                        used_selected = normalize_clause_for_compare(step[1])
                        used_pairs.add((used_sos, used_selected))

                    # Keep clauses that are not present in used_pairs for (sos, clause)
                    valid_clauses = sorted(
                        [
                            clause for clause in potential_clauses
                            if (norm_sos, normalize_clause_for_compare(clause)) not in used_pairs
                        ],
                        key=len
                    )
                    print("Potential Clauses: ", potential_clauses)
                    print("Valid Clauses: ", valid_clauses)
                    
                    if valid_clauses:
                        if len(valid_clauses) > 1:
                            list_of_sos.append(sos_list)
                            list_of_compelment.append(valid_clauses)
                            print("Current SOS: ", sos_list, "Current Complement: ", valid_clauses)
                            selected_clause = list_of_compelment[-1].pop(0)
                        else:
                            selected_clause = valid_clauses[0]
                    else:
                        print("All potential clauses have been used before with this SOS list.")
                        print("Checking cached SOS and complement pairs.")
                        print(f"List of Complements in Cache: {list_of_compelment} with length: {len(list_of_compelment)}" )
                        found_new_pair = False
                        if len(list_of_compelment) > 0:
                            for i, complement_clauses in enumerate(list_of_compelment):
                                if complement_clauses:
                                    sos_list = list_of_sos[i]
                                    selected_clause = complement_clauses.pop(0)
                                    found_new_pair = True
                                    break
                            if not found_new_pair:
                                print("No more sos and complement pairs found in cache.")
                                final_answer = "cannot find sos with complement"
                                break

                if not complement_indices:
                    if len(list_of_compelment) > 0:
                        all_empty = True
                        original_sos = sos_list
                        original_selected_clause = selected_clause
                        for i, clauses in enumerate(list_of_compelment):
                            if len(clauses) > 0:
                                new_selected_clause = list_of_compelment[i][0]
                                new_sos_list = list_of_sos[i]
                                if new_sos_list != original_sos or new_selected_clause != original_selected_clause:
                                    selected_clause = list_of_compelment[i].pop(0)
                                    sos_list = new_sos_list
                                    all_empty = False 
                                    print("Check cache: ", sos_list, "Current Complement: ", selected_clause)
                                    break
                        if all_empty:
                            final_answer = "No complement found in both context and cache."
                            break
                    else: 
                        final_answer = "No complement found in the context."
                        break

            if any(                        
                normalize_clause_for_compare(step[0]) == normalize_clause_for_compare(sos_list) and
                normalize_clause_for_compare(step[1]) == normalize_clause_for_compare(selected_clause)
                for step in reasoning_step):
                print("Skipping this search round as it has appeared before.")
                found_new_pair = False
                for i, complement_clauses in enumerate(list_of_compelment):
                    if complement_clauses:
                        new_sos_list = list_of_sos[i]
                        new_selected_clause = complement_clauses[0]
                        if new_sos_list != sos_list or new_selected_clause != selected_clause:
                            sos_list = new_sos_list
                            selected_clause = complement_clauses.pop(0)
                            found_new_pair = True
                            break

                if not found_new_pair:
                    print("No more sos and complement pairs found in cache.")
                    final_answer = "No sos and complement found"
                    break 
            else:
                print("SOS: ", sos_list)
                print("Selected Clause: ", selected_clause)
                print("Search round: ", search_round)
            
            # If after all selection attempts we still have no selected_clause, abort gracefully
            if selected_clause is None:
                print("No selected_clause available after checking context and cache. Aborting example as Unknown.")
                final_answer = "Unknown"
                flag = 'false'
                break
            prompts_e = self.construct_prompt_e(negated_label, normalized_conjecture, sos_list, selected_clause, in_context_examples_logic_resolver)
            print(f"\n\nPrompt to Logic Solver: {prompts_e}\n\n", )
            responses_e, _ = self.model_api.generate(prompts_e)
            print(f"\n\nResponse from Logic Solver: {responses_e}\n\n", )
            
            logic_solver_result = self.post_process_logic_solver(responses_e)
            new_clause = logic_solver_result['new_clause']
            sufficiency_label = logic_solver_result['sufficiency_label']
            
            solve_step = [sos_list, selected_clause, new_clause]
            
            reasoning_step.append(solve_step)
            print('Reasoning Steps:')
            for step in reasoning_step:
                sos_list, selected_clause, new_clause = step
                solving_step = f"SOS clause: {sos_list}. Selected Clause: {selected_clause}. New Clause: {new_clause}"
                print(solving_step)
            
            if not new_clause.strip():
                print("No new clause found. Searching from the cache.")
                all_empty = "True"
                for i, clause in enumerate(list_of_compelment):
                    if len(clause) > 0:
                        selected_clause = list_of_compelment[i].pop(0)
                        sos_list = list_of_sos[i]
                        all_empty = "False"
                        print("Searching from cache: Current SOS: ", sos_list, "Current Complement: ", selected_clause)
                        break
                        
                if len(list_of_compelment) > 0 and all_empty == "True": 
                    final_answer = "Unknown"
                    flag = 'false'
                elif len(list_of_compelment) == 0:
                    final_answer = "Unknown"
                    flag = 'false'
            else:
                sos_list = new_clause
                normalized_context_list.append(new_clause)
                selected_clause = None
            
            if sufficiency_label == "True":
                if new_clause and (new_clause.lower() == "kontradiksi" or new_clause.lower() == "false"):
                    if negated_label.lower() == "true":
                        final_answer = "True"
                    elif negated_label.lower() == "false":
                        final_answer = "False"

                    flag = 'false'
                
                else: 
                    all_empty = "True"
                    for i, clause in enumerate(list_of_compelment):
                        if len(clause) > 0:
                            selected_clause = list_of_compelment[i].pop(0)
                            sos_list = list_of_sos[i]
                            all_empty = "False"
                            print("Check Cache: ", sos_list, "Current Complement: ", selected_clause)
                            break
                        
                    if len(list_of_compelment) > 0 and all_empty == "True":
                        final_answer = "Unknown"
                        flag = 'false'
                    elif len(list_of_compelment) == 0:
                        final_answer = "Unknown"
                        flag = 'false'

            search_round += 1
            
        final_choice = self.final_process(final_answer)
        
        output = {'id': example['id'], 
                'original_context': example['original_context'],
                'question': example['question'], 
                'translated_context': example['translated_context'],
                'normalized_context': example['normalized_context'],
                'normalized_conjecture': example['normalized_conjecture'],
                'negated_label': negated_label,
                'reasoning_step': self.list_to_indexed_string(reasoning_step),
                'ground_truth': example['ground_truth'], 
                'final_answer': final_answer,
                'final_choice': final_choice,
                'search_round': search_round}
        
        print(output)
        return output