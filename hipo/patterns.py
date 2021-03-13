import random
from pattern import Pattern, Sentiment, Usefulness


class PatternCollection(list):
    def __init__(self, *items: Pattern):
        super().__init__()
        self.extend(items)

    def id_of(self, item: Pattern) -> float:
        return float(f'{item.code}.{self.index(item)}') / 2

    def choose(self, count: int):
        _self = self[:]
        random.shuffle(_self)
        collected_patterns = []
        pattern: Pattern
        for pattern in _self:
            if pattern.code not in [p.code for p in collected_patterns]:
                collected_patterns.append(pattern)
            if len(collected_patterns) == count:
                break
        else:
            raise ValueError(f'not enough patterns defined to select {count} try {len(set([p.code for p in self]))}')
        return collected_patterns


patterns = PatternCollection(
    Pattern('Esik az eső', sentiment=Sentiment.NEGATIVE, usefulness=Usefulness.IRRELEVANT, precondition='nincs',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat során kint esett az eső.'),
    Pattern('Süt a nap', sentiment=Sentiment.POSITIVE, usefulness=Usefulness.IRRELEVANT, precondition='nincs',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat során nem volt felhő az égen és sütött a nap.'),
    Pattern('Szoba színe', sentiment=Sentiment.NATURAL, usefulness=Usefulness.IRRELEVANT,
            precondition='Ha a vsz. a vizsgálat során...',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladatot egy egyszínű TBA festett teremben kellett megoldani.'),
    Pattern('Eclipse összeomlik', sentiment=Sentiment.NEGATIVE, usefulness=Usefulness.HARMFUL,
            precondition='A felhasználó legalább 2 percig vizsgálja a $(metódus)-t.',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat során, miközben a $(metódus)-t olvassa az Eclipse fejlesztő környezet összeomlik és újra kell indítani, minden megnyitott fájl becsukódik és a módosítások elvesznek.'),
    Pattern('Hibák listája lassan töltődik be', sentiment=Sentiment.NEGATIVE, usefulness=Usefulness.HARMFUL,
            precondition='A felhasználó megnyitja és megvizsgálja a hibák listáját az Eclipseben.',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat során, amikor a projekben lévő hibákat szerette volna vizsgálni a lista betöltése 5 percet vesz igénybe. Eközben az Eclipse fejlesztő környezet nem reagál az utasításokra.'),
    Pattern('Bekopognak a terembe', sentiment=Sentiment.NATURAL, usefulness=Usefulness.HARMFUL, precondition='nincs',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat során valaki bekopog a terembe és ajtót kell nyitni, de tévedés volt.'),
    Pattern('Csivitelnek a madarak', sentiment=Sentiment.NATURAL, usefulness=Usefulness.HARMFUL, precondition='Nincs',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat során az ablakban ült egy madár aminek a csipogása 10-15 percenként behallatszik.'),
    Pattern('Kedves ismerőse vagy családtagja telefonál', sentiment=Sentiment.POSITIVE, usefulness=Usefulness.HARMFUL,
            precondition='nincs',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat közben felhívja egy kedves ismerőse, családtagja vagy barátja akivel már nagyon régen nem beszéltek, hogy megkérdezze hogy mi újság Önnel.'),
    Pattern('Nyeremény', sentiment=Sentiment.POSITIVE, usefulness=Usefulness.HARMFUL, precondition='nincs',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat közben, felhívja egy közvetítő és értesíti, hogy egy régóta vágyott tárgyat nyert egy játék keretében.'),
    Pattern('A metódust tapasztalatlan kollega írta', sentiment=Sentiment.NATURAL, usefulness=Usefulness.HELPFUL,
            precondition='Ha a vsz. a vizsgálat során legalább 2 percig vizsgálja a $(metódus)-t.',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat előtt, egy megbeszélésen hallotta, hogy a $(metódus)-t egy fiatal, kezdő és kevés tapasztalattal rendelkező kolléga készítette el egyedül.'),
    Pattern('A osztályt tapasztalatlan kollega írta', sentiment=Sentiment.NATURAL, usefulness=Usefulness.HELPFUL,
            precondition='Ha a vsz. a vizsgálat során legalább 6 percig vizsgálja a $(osztály)-t.',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat előtt, egy megbeszélésen hallotta, hogy a $(osztály)-t egy fiatal, kezdő és kevés tapasztalattal rendelkező kolléga készítette el egyedül.'),
    Pattern('A metódust tapasztalat kollega írta', sentiment=Sentiment.NATURAL, usefulness=Usefulness.HELPFUL,
            precondition='Ha a vsz. a vizsgálat során legalább 2 percig vizsgálja a $(metódus)-t.',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat előtt, egy megbeszélésen hallotta, hogy a $(metódus)-t egy senior, a projektet részletesen ismerő és sok tapasztalattal rendelkező kolléga készítette el egyedül.'),
    Pattern('A osztályt tapasztalat kollega írta', sentiment=Sentiment.NATURAL, usefulness=Usefulness.HELPFUL,
            precondition='Ha a vsz. a vizsgálat során legalább 6 percig vizsgálja a $(osztály)-t.',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat előtt, egy megbeszélésen hallotta, hogy a $(osztály)-t egy senior, a projektet részletesen ismerő és sok tapasztalattal rendelkező kolléga készítette el egyedül.'),
    Pattern('Megfelelő ábra a dokumentációban', sentiment=Sentiment.NATURAL, usefulness=Usefulness.HELPFUL,
            precondition='Ha a vsz. a vizsgálat során legalább 2 percig kereste, hogy a $(metódus)-t ki hívja vagy az kit hív.',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat közben a fejlesztői kézikönyvben vagy dokumentációban talált egy diagramott ami részletesen bemutatja, hogy a $(metódus) milyen kapcsolatban van a többi metódussal, melyik hívja melyiket és miért.'),
    Pattern('Egyik kolléga segít megérteni az adott metódust', sentiment=Sentiment.POSITIVE,
            usefulness=Usefulness.HELPFUL,
            precondition='Ha a vsz. a vizsgálat során legalább 2 percig vizsgálja a $(metódus)-t.',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat a munkahelyén oldotta meg. Ebéd előtt a $(metódus)-t kezdte el átnézni. Az ebéd szünetben beszélgettek erről az egyik kollégájával aki felajánlotta, hogy segít megérteni, hogy mit csinál a $(metódus)-t. '),
    Pattern('Egyik kolléga segít megérteni az adott osztályt', sentiment=Sentiment.POSITIVE,
            usefulness=Usefulness.HELPFUL,
            precondition='Ha a vsz. a vizsgálat során legalább 6 percig vizsgálja a $(osztály)-t.',
            change='Tegyük fel, hogy a legutóbbi alkalomon megoldott feladat a munkahelyén oldotta meg. Ebéd előtt az $(osztály)-t kezdte el átnézni. Az ebéd szünetben beszélgettek erről az egyik kollégájával aki felajánlotta, hogy segít megérteni, hogy mire szolgál az adott osztály.')
)
