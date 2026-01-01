:- use_module(library(tabling)).
:- style_check(-discontiguous).
:- style_check(-singleton).

:- dynamic agresif/1, neg_agresif/1, asam/1, neg_asam/1, dumpus/1, neg_dumpus/1, impus/1, neg_impus/1, jompus/1, neg_jompus/1, kayu/1, neg_kayu/1, kecil/1, neg_kecil/1, merah/1, neg_merah/1, numpus/1, neg_numpus/1, pemalu/1, neg_pemalu/1, rompus/1, neg_rompus/1, tanah/1, neg_tanah/1, tembuspandang/1, neg_tembuspandang/1, tumpus/1, neg_tumpus/1, vumpus/1, neg_vumpus/1, wumpus/1, neg_wumpus/1, yumpus/1, neg_yumpus/1, zumpus/1, neg_zumpus/1.
:- table agresif/1, neg_agresif/1, asam/1, neg_asam/1, dumpus/1, neg_dumpus/1, impus/1, neg_impus/1, jompus/1, neg_jompus/1, kayu/1, neg_kayu/1, kecil/1, neg_kecil/1, merah/1, neg_merah/1, numpus/1, neg_numpus/1, pemalu/1, neg_pemalu/1, rompus/1, neg_rompus/1, tanah/1, neg_tanah/1, tembuspandang/1, neg_tembuspandang/1, tumpus/1, neg_tumpus/1, vumpus/1, neg_vumpus/1, wumpus/1, neg_wumpus/1, yumpus/1, neg_yumpus/1, zumpus/1, neg_zumpus/1.

yumpus(max).

neg_pemalu(X) :- jompus(X).
yumpus(X) :- jompus(X).
agresif(X) :- yumpus(X).
dumpus(X) :- yumpus(X).
neg_kayu(X) :- dumpus(X).
wumpus(X) :- dumpus(X).
merah(X) :- wumpus(X).
impus(X) :- wumpus(X).
neg_tembuspandang(X) :- impus(X).
tumpus(X) :- impus(X).
asam(X) :- numpus(X).
neg_asam(X) :- tumpus(X).
vumpus(X) :- tumpus(X).
tanah(X) :- vumpus(X).
zumpus(X) :- vumpus(X).
kecil(X) :- zumpus(X).
rompus(X) :- zumpus(X).


:- initialization(main).

main :-
    % catch/3 ensures that even a runtime error won't hang the script
    catch((
        ( once(asam(max)) -> PT=true ; PT=false ),
        ( once(neg_asam(max)) -> PF=true ; PF=false ),
        ( PT==true, PF==true -> Conflict=true ; Conflict=false ),
        format('PROLOG_RESULT|~w|~w|~w~n', [PT, PF, Conflict])
    ), _Error, (
        % If an error happens, we still report false and exit
        format('PROLOG_RESULT|false|false|false~n')
    )),
    halt.
