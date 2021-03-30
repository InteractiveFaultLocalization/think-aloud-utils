import sys

from patterns import patterns

if __name__ == '__main__':
    with open('use_cases.html', 'w', encoding='utf8') as f:
        f.write('<html><body>')
        for i in range(6):
            f.write(f'<p style="font-style: italic">Vsz. azonosító (szám): {i+1}</p>')
            f.write('<p>A vv. olvassa fel mindegyik eset azonosítóját.<br/>'
                    'Esetenként 10 perc áll rendelkezésre.<br/>'
                    '<span style="font-weight: bold">A vv. nem foglalhat állást az esetekkel kapcsolatban.</span><br/>'
                    'A rögzítés miatt nincs szükség jegyzetelésre!</p>')
            for pattern in patterns.choose(int(sys.argv[1])):
                f.write(f'<p>{pattern.short_txt(patterns)}</p>')
            f.write('<p style="page-break-after: always; text-align: center">vége</p>')
        f.write('</body></html>')

