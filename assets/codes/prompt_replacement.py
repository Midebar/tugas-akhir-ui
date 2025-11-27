def construct_prompt_a(self, record, in_context_examples_trans):
    full_prompt = in_context_examples_trans
    if self.dataset_name == "LogicNLI":
        context = "\n".join(record['facts'] + record['rules'])
        question = record['conjecture']
    else:
        context = record['context']
        question = re.search(r'\?(.*)', record['question'].strip()).group(1).strip()
    full_prompt = full_prompt.replace('[[PREMISES]]', context)
    full_prompt = full_prompt.replace('[[CONJECTURE]]', question)
    return full_prompt