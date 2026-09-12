"""Photograph-led transcription of printed pages 185–204.
Original page breaks, blank fields and apparent source errors retained.
"""
from .parts_tables import row
from .opening_tables import entry,component,composed
from .tables_045_064 import assembly
from .tables_065_084 import pieces,stacked
TABLES={}
def start(page):
 TABLES[page]=[]
 return TABLES[page]
def add(page,content):
 r=start(page)
 append_rows(r,content)
 return r
def append_rows(r,content):
 for line in content.strip().splitlines():
  values=line.split('|');assert len(values)==9,line
  r.append(row(*[v.replace('~','\n') for v in values]))

r=add(185,'''||||||   M2126 (1); plate M2737 strap M2780 and bracket M2127 (1); plate M2748 strap~   M2780 and bracket M2126 (1); plate M3777 angle M3788 and angle M3789A (1);~   plate M3778 angle M3800 and angle M3789B (1); plate M3780A angle M3791A~   and angle M3790A (1); plate M3780B angle M3791B and angle M3790B (1);~   cleat M1946A (2); cleat M1947 (2); cleat M1945A (2); cleat M1945B (2); cleat~   M1946B (2).)|651|$0.02 P
&(sh)R||||||RIVET, button head, 11/16″ x 2½″.  (For plate M1963B beam M2039B and strap~   M2000 (1); plate M1963A beam M2039A and strap M2000 (1); plate M1963B~   beam M2016B and strap M2000 (1); plate M1963A beam M2016A and strap~   M2000 (1); plate M1963B strap M2000 and angle M2007B (6); plate M1963A~   strap M2000 and angle M2007A (6); plate M1963B strap M2006 and angle M2007B~   (1); plate M1963A strap M2006 and angle M2007A (1); plate M1996A and hinge~   M2827 (1); plate M1996A and hinge M2828 (1); plate M1996B and hinge M2827~   (1); plate M1996B and hinge M2828 (1); plate M1964A beam M2039B and strap~   M1995 (1); plate M1964B beam M2039A and strap M1995 (1); plate M2033 plate~   M2014 and angle M2075 (7); plate M1965 angle M2007B and strap M2006 (12);~   plate M1965 angle M2007A and strap M2006 (12); plate M1966 angle M2007B~   and strap M2006 (9); plate M1966 angle M2007A and strap M2006 (9); plate~   M1970B angle M2007B and strap M2006 (4); plate M1970A angle M2007A and~   strap M2006 (4); plate M1969 angle M2017 and strap M2006 (8); plate M1969~   angle M2007A and strap M2006 (8); plate M1971B angle M2007B and strap M2006~   (10); plate M1971A angle M2007A and strap M2006 (10); plate M1973 angle~   M2007B and strap M2006 (5); plate M2070 angle M2007A and strap M2006 (5);~   plate M1973 angle M2007B and strap M1994B (5); plate M2070 angle M2007A~   and strap M1994A (5); plate M1970A beam M2047 through (2) hinges M706~   (2); plate M1970B beam M2029 through (2) hinges M706 (2); plate M1971A~   strap M2049 and angle M2141A (3); plate M1971B strap M2049 and angle~   M2141B (3); plate M1967A angle M2019A and plate M1979 (3); plate M1967B~   angle M2019B and plate M1979 (3); plate M1973 plate M1979 and angle M2019B~   (1); plate M2070 plate M1979 and angle M2019A (1); plate M1973 angle M2118~   and angle M2019B (1); plate M2073 angle M2119 and angle M2019A (1); plate~   M1979 plate M1971B and beam M2041 (1); plate M1979 plate M1971A and strap~   M2046 (1); plate M1979 plate M1971B and angle M2062B (1); plate M1979 plate~   M1971A and angle M2062A (1); plate M1973 plate M1979 and strap M2046 (1);~   plate M2070 plate M1979 and beam M2041 (1); plate M1989A plate SH294A~   and angle M1921A (2); plate M1989B plate SH294A and angle M1921B (2); angle~   M2061B plate M1988 and angle M2063B (1); angle M2061A plate M1988 and~   angle M2063A (1); angle M2061A angle M2062B and plate M1986 (1); angle~   M2061B angle M2062A and plate M1986 (1); strut M2121 angle M2019B and||''')

r=add(186,'''&(sh)R||||||RIVET, button head, 11/16″ x 2½″—Continued.~   plate M1973 (1); strut M2120 angle M2019A and plate M2070 (1); strut M2121~   strap M2043 and plate M1973 (1); strut M2120 beam M2042 and plate M2070~   (1); plate M1990 angle M2019B and strut M2125 (1) plate M1990 angle M2019A~   and strut M2124 (1); plate M1990 angle M2044B and strut M2125 (1); plate M1990~   angle M2044A strut M2124 (1); plate M2096 angle M2101B and angle M2103B~   (1); plate M2096 angle M2101A and angle M2103A (1); plate M2096 angle M2102B~   and angle M2101B (1); plate M2096 angle M2102A and angle M2101A (1); plate~   M2095 angle M2105A and plate M2003 (1); plate M2095 angle M2105B and plate~   M2003 (1); plate M2098 angle M2105A and strap M2099A (1); plate M2098 angle~   M2105B and strap M2099B (1); plate M2098 angle M2101A and strap M2099A (1);~   plate M2098 angle M2101B and strap M2099B (1); plate M2097 angle M2101A~   and strap M2099A (1); plate M2097 angle M2101B and strap M2099B (1); plate~   M2097 angle M2104A and strap M2099A (1); plate M2097 angle M2104B and~   strap M2099B (1); plate M2095 angle M2104A and strap M2003 (4); plate M2095~   angle M2104B and strap M2003 (4); plate M1977 angle M2106A and angle M1972A~   plate M1977 angle M2106B and angle M1972B (1); plate M1977 angle M2106B~   and angle M2027B (1); plate M1977 angle M2106A and angle M2027A (1); plate~   M2095 angle M2044A and plate M2003 (3); plate M2095 angle M2044B and~   plate M2003 (3); plate M2095 angle M1913 and plate M2003 (5); plate M1939~   angle M1943 plate M1938 and angle M2018B (1); plate M1939 angle M1943 plate~   M1938 and angle M2018A (1); plate M1933 angle M2018B beam M1941 and~   piece M2086 (1); plate M1933 angle M2018A beam M1941 and piece M2086 (1);~   plate M1933 angle M2017B beam M1941 and piece M2086 (1); plate M1933~   angle M2017A beam M1941 and piece M2086 (1); plate M1932 angle M2018B~   and beam M1941 (1); plate M1932 angle M2018A and beam M1941 (1); plate~   M1932 angle M2017B and beam M1941 (1); plate M1932 angle M2017A and~   beam M1941 (1); plate M1932 angle M2007B and angle M2008B (6); plate M1932~   angle M2007A and angle M2008A (6); plate M1932 angle M2018B and strap~   M1940 (1); plate M1932 angle M2018A and strap M1940 (1); plate M1932 angle||''')

r=add(187,'''||||||   M2017B and strap M1940 (1); plate M1932 angle M2017A and strap M1940~   (1); plate M1931 angle M2018B and strap M1940 (1); plate M1931 angle M2018A~   and strap M1940 (1); plate M1931 angle M2017B and strap M1940 (1); plate~   M1931 angle M2017A and strap M1940 (1); plate M1931 angle M2007B and~   angle M2008B (6); plate M1931 angle M2007A and angle M2007A (6); plate~   M1903 plate M1924 and bracket M3922 (4); plate M1915A packing M2109 chan-~   nel M2108 and strap M1919 (9); plate M1915A packing M2109 channel M2108~   and beam M1900 (1); plate M1915A packing M2109 channel M2108 and beam~   M1913 (1); packing M2350 angle M2395 and bracket M2439B (2); plate M2348~   angle M2395 and bracket M2439A (2); plate M2351 angle M2397 and bracket~   M2440B (2); plate M2349 angle M2396 and bracket M2440A (2); plate M2743~   strap M2787 and angle M2803 (1); plate M2743 strap M2787 and angle M2804~   (1); plate M2745 strap M2788 and angle M2806 (1); plate M2745 strap M2788~   and angle M2805 (1); plate M2733 strip M2810 and angle M3788 (7); plate M2733B~   strip M2810 and angle M3800 (7); plate M2733A plate SH491A and angle M3788~   (1); plate M2733B plate SH492A and angle M3800 (1); plate M2736 plate~   SH491A and angle M3788 (5); plate M2747 plate SH492A and angle M3800 (6);~   plate M2737 plate SH491A and angle M3788 (2); plate M2737 plate SH491A~   and angle M2780 (1); plate M2748 plate SH492A and angle M2780 (1); plate~   M2738 strap M2780 and plate SH491A (1); plate M2738 strap M2780 and plate~   SH492A (1); plate M2738 plate SH491A strap M2781A (1); plate M2738 plate~   SH492A and strap M2781B (1); plate M2739 plate SH491A and strap M2786A~   (1); plate M2750 plate SH492A and strap M2786B (1); plate M2744 angle M2807~   and strap M2789 (1); plate M2744 angle M2808 and strap M2789 (1).)|331|$0.02 P
&(sh)R||||||RIVET, button head, 11/16″ x 2⅝″.  (For plate M2033 plate M2014 and angle~   M1893A (3); plate M2033 plate M2014 and angle M1893B (3); plate M2033 plate~   M2014 and angle M1950 (8); plate M1976B angle M2004B and angle M2118 (1);~   plate M1976A angle M2004A and angle M2119 (1); plate M2021 angle M2023A and~   angle M2022A (5); plate M2021 angle M2023B and angle M2022B (5); plate M1938~   angle M2007B angle M2008B and beam M1930 (1); plate M1938 angle M2007A~   angle M2008A and beam M1930 (1); plate M1937 angle M2007B angle M2008B~   and beam M1930 (1); plate M1937 angle M2007A angle M2008A and beam M1930~   (1); plate M1937 angle M2007B angle M2008B and beam M1929 (1); plate M1937~   angle M2007A angle M2008A and beam M1929 (1); plate M1936 angle M2007B~   angle M2008B and beam M1929 (1); plate M1936 angle M2007A angle M2008A~   and beam M1929 (1); plate M1936 angle M2007B angle M2008B and angle M1942B~   (1); plate M1936 angle M2007A angle M2008A and angle M1942B (1); plate M1935~   angle M2007B angle M2008B and angle M1942A (1); plate M1935 angle M2007A~   angle M2008A and angle M1942A (1); plate M1935 angle M2007B angle M2008B||''')

r=add(188,'''&(sh)R||||||RIVET, button head, 11/16″ x 2⅝″—Continued.~   and beam M1928 (1); plate M1935 angle M2007A angle M2008A and beam M1928~   (1); plate M1934 angle M2007B angle M2008B and beam M1928 (1); plate M1934~   angle M2007A angle M2008A and beam M1928 (1); plate M1934 angle M2007B~   angle M2008B and beam M1927 (1); plate M1934 angle M2007A angle M2008A~   and beam M1927 (1); plate M1933 angle M2007B angle M2008B and beam M1927~   (1); plate M1933 angle M2007A angle M2008A and beam M1927 (1); plate M2395~   angle M2415A and plate M2363 (1); plate M2395 angle M2415B and plate M2363~   (1); plate M2363 angle M2420A and angle M2418A (1); plate M2363 angle M2420B~   and angle M2418B (1); plate M2362 angle M2420A and angle M2417 (1); plate~   M2362 angle M2420B and angle M2417 (1); plate M2350 angle M2395 and angle~   M2390B (1); plate M2348 angle M2395 and angle M2390A (1); plate M2350 angle~   M2383B and batten M2385B (1); plate M2348 angle M2383A and batten M2385A~   (1); plate M2350 strap M2422 and batten M2386 (1); plate M2348 strap M2422 and~   batten M2386 (1); plate M2350 angle M2390B and strap M2422 (1); plate M2348~   angle M2390A and strap M2422 (1); plate M2354 batten M2386 and strap M2422~   (2); plate M2354 angle M2390B through (2) straps M2422 (2); plate M2354 angle~   M2390A through (2) straps M2422 (2); plate M2351 angle M2390B and strap~   M2422 (1); plate M2349 angle M2390A and strap M2422 (1); plate M2351 batten~   M2422 and strap M2422 (1); plate M2349 batten M2386 and strap M2422 (1); plate~   M2349 angle M2384 and batten M2385B (1); plate M2351 angle M2408 and batten~   M2385A (1); plate M2351 plate SH395D plate SH409A (2); plate M2351 angle~   M2397 and angle M2390B (1); plate M2349 angle M2396 and angle M2390A (1);~   plate M2407 angle M2397 and angle M2381 (1); plate M2406 angle M2396 and angle~   M2381 (1); plate M3777 plate M3779A and angle M3792 (2); plate M3778 plate~   M3779B and angle M3793 (2); plate M3778 angle M3791B and plate M3779B (1);~   hinge M706 to side door left and right (1); transmission frame, assembly (12).)|104|$0.02 P
&(sh)R||||||RIVET, button head, 11/16″ x 2¾″.  (For plate M1996A and hinge M2827 (2);~   plate M1996A and hinge M2828 (2); plate M1996B and hinge M2827 (2); plate~   M1996B and hinge M2828 (2); plate M1970A beam M2047 and bracket SH395B (1);||''')

r=add(189,'''||||||   plate M1970A beam M2047 and bracket SH395A (1); plate M1970B beam M2029~   and bracket SH395B (1); plate M1970B beam M2029 and bracket SH395A (1);~   piece M2036 stiffener M2035 plate M1992 and angle M2019B (21); piece M2036~   stiffener M2035 plate M1992 and angle M2019A (21); angle M2061A plate M1987~   angle M2141A and plate M2137 (1); angle M2061B plate M1987 angle M2141B~   and plate M2137 (1); strap M2177 plate M1975B angle M2019B and strut M2133~   (1); strap M2177 plate M1975A angle M2019A and strut M2122 (1).)|58|.02 P
&(sh)R||||||RIVET, button head, 11/16″ x 2⅞″.  (For plate M1967B angle M2019B plate~   M1979 and bracket M2130 (1); plate M1967A angle M2019A plate M1979 and~   bracket M2131 (1); plate M1967B angle M2062B plate M1979 and bracket M2130~   (1); plate M1967A angle M2062A plate M1979 and bracket M2131 (1); plate M2003~   angle M2105A plate M2095 and angle M2044A (1); plate M2003 angle M2105B~   plate M2095 and angle M2044B (1); plate M1932 strap M1940 angle M2007B and~   angle M2008B (1); plate M1932 strap M1940 angle M2007A and angle M2008A~   (1); plate M1931 strap M1940 angle M2007B and angle M2008B (1); plate M1931~   strap M1940 angle M2007A and angle M2008A (1); plate M1931 angle M2018B~   and angle M1950 (1); plate M1931 angle M2018A and angle M1950 (1); plate~   M1931 angle M2017B and angle M1950 (1); plate M1931 angle M2017A and angle~   M1950 (1); plate M1903 plate M1924 bracket M3922 and angle M1895 (2); plate~   M1933 beam M1941 piece M2086 angle M2007B and angle M2008B (1); plate~   M1933 beam M1941 piece M2086 angle M2007A and angle M2008A (1); plate~   M1932 beam M1941 angle M2007B and angle M2008B (1); plate M1932 beam~   M1941 angle M2007A and angle M2008A (1).)|20|.02 P
&(sh)R||||||RIVET, button head, 11/16″ x 3″.  (For hinge M706 to side door left and right~   (2).)|8|.03 P
&(sh)R||||||RIVET, button head, 11/16″ x 3¼″.  (For plate M1963B piece M2036 stiffener~   M2035 and angle M2019B (8); plate M1963A piece M2036 stiffener M2035 and~   angle M2019A (8); plate M1970B angle M2019B piece M2036 and stiffener M2035~   (4); plate M1970A angle M2019A piece M2036 and stiffener M2035 (4); plate~   M1967B angle M2019B piece M2036 and stiffener M2035 (9); plate M1967A~   angle M2019A piece M2036 and stiffener M2035 (9).)|42|.02 P
&(sh)R||||||RIVET, button head, 11/16″ x 3¾″.  (For plate M2739 strip M2798 and lug M2839~   (1); plate M2750 strip M2798 and lug M2839 (1).)|2|.02 P
&(sh)R||||||RIVET, button head, ¾″ x 1⅝″.  (For strap M2001 (left) (3); strap M2001~   (right) (4).)|7|.02 P
&(sh)R||||||RIVET, button head, ¾″ x 2⅛″.  (For strap M2001 (left) (7); strap M2001 (right)~   (4); rim M1471 (24); rim M1401 (24).)|203|.02 P
&(sh)R||||||RIVET, button head, ¾″ x 2½″.  (For plate M1978 and bearing M1546 (6).)|12|.02 P
&(sh)R||||||RIVET, button head, ¾″ x 2⅝″.  (For plate M1977 and bearing M1406 (6).)|12|.02 P''')

r=add(190,'''&(sh)R||||||RIVET, button head, ⅞″ x 2¼″.  (For bracket M3918 and plate M1939 (5).)|5|$0.02 P
&(sh)R||||||RIVET, button head, ⅞″ x 2½″.  (For bracket M3917 and plate M1931 (4);~   bracket M3917 strap M1994B strip M2002 and angle M2007B (3); bracket M3917~   strap M1994A strip M2002 and angle M2007A (3).)|10|.02 P
&(sh)R||||||RIVET, button head, ⅞″ x 2⅝″.  (For plate M1939 angle M2025 and bracket~   M3918 (2).)|2|.02 P
&(sh)R||||||RIVET, button head, ⅞″ x 2¾″.  (For plate M2021 and bracket M3818 (5).)|5|.03 P
&(sh)R||||||RIVET, button head, ⅞″ x 2⅞″.  (For bracket M3917 plate M1931 and angle~   M1950 (2).)|2|.03 P
&(sh)R||||||RIVET, button head, ⅞″ x 3″.  (For plate M2021 angle M2025 and bracket~   M3918 (2).)|2|.03 P
&(sh)R||||||RIVET, button head, ⅞″ x 3⅛″.  (For bracket M3917 plate M2033 and plate~   M2014 (5); bracket M3919 strap M1994B angle M2000B and plate M1985 (3);~   bracket M3919 strap M1994A angle M2008A and plate M1985 (3).)|11|.04 P
&(sh)R||||||RIVET, button head, ⅞″ x 3½″.  (For bracket M3917 plate M2033 plate M2014~   and angle M1950 (2).)|2|.04 P
X|||D23298|||RIVET, button head, brass, 5/64″ x .144″.  (For generator brush arm D13829 (2).)|8|.01 P
X|||D25461|||RIVET, button head, brass, .091″ x .191″.  (For voltage regulator, assembly~   D5718 (1).)|1|.01 P
X|||D26824|||RIVET, button head, brass, .107″ x .157″.  (For distributor shaft, assembly~   D13899 (1).)|2|.01 P
&(sh)R||||||RIVET, button head, copper, ⅛″ x ⅜″.  (For hinge SH942F (3).)|12|.01 P
X|||D29767|||RIVET, countersunk head, .061″ x .141″.  (For distributor contact spring D13803~   (2).)|8|.01 P
&(sh)R||||||RIVET, countersunk head, ⅛″ x ½″.  (For clip M2835 (3).)|12|.01 P
&(sh)R||||||RIVET, countersunk head, 3/16″ x ½″.  (For ammunition storage (above rear~   shell storage) (52); removable platform storage, assembly (12); platform ammu-~   nition storage (Browning machine gun), assembly (31).)|95|.01 P
&(sh)R||||||RIVET, countersunk head, 3/16″ x 9/16″.  (For arm X259 (4).)|8|.01 P''')

r=add(191,'''&(sh)R||||||RIVET, countersunk head, 3/16″ x ⅝″.  (For ammunition storage (above rear~   shell storage), assembly (426); beading M1585 (5); removable platform storage,~   assembly (250); platform ammunition storage (Browning machine gun), as-~   sembly (386).)|1,082|.01 P
&(sh)R||||||RIVET, countersunk head, 3/16″ x ⅞″.  (For platform ammunition storage~   (Browning machine gun), assembly (3).)|3|.01 P
&(sh)R||||||RIVET, countersunk head, 3/16″ x 1″.  (For piece 14X90 (2); platform ammuni-~   tion storage (Browning machine gun), assembly (6); cleat SH291F (10).)|56|.01 P
&(sh)R||||||RIVET, countersunk head, ¼″ x ⅞″.  (For platform ammunition storage~   (Browning machine gun), assembly (2).)|2|.01 P
&(sh)R||||||RIVET, countersunk head, ¼″ x ⅝″.  (For hinge M2158 (3).)|6|.01 P
&(sh)R||||||RIVET, countersunk head, ¼″ x 1″.  (For stop SH293E (2); platform ammuni-~   tion storage (Browning machine gun), assembly (7).)|15|.01 P
&(sh)R||||||RIVET, countersunk head, ¼″ x 1 3/16″.  (For lug MX86 (3); lug MX87 (3).)|12|.01 P
&(sh)R||||||RIVET, countersunk head, 5/16″ x 1″.  (For end M361 (6).)|12|.01 P
&(sh)R||||||RIVET, countersunk head, 5/16″ x 1⅛″.  (For band M359 (3); band M360 (3).)|12|.01 P
&(sh)R||||||RIVET, countersunk head, 5/16″ x 1¼″.  (For plate 3X90 (2).)|40|.01 P
&(sh)R||||||RIVET, countersunk head, ⅜″ x 1⅜″.  (For ear MX48 (8); bracket MX49 (8);~   bracket MX47 (7); ear MX46 (6); plate M2737 and plate M2845 (4); plate M2748~   and plate M2845 (4); plate M2739 and plate M2845 (4); plate M2750 and plate~   M2845 (4); plate M2745 and plate M2845 (4); plate M2743 and plate M2845 (4);~   plate M2744 and plate M2844 (4).)|144|.01 P
&(sh)R||||||RIVET, countersunk head, ⅜″ x 1½″.  (For plate M2362 and plate M2845 (4);~   plate M2387 and plate M2845 (4); plate M2388 and plate M2845 (4); plate M2348~   and plate M2845 (4); plate M2349 and plate M2845 (4); plate M2351 and plate~   M2845 (4); plate M2350 and plate M2845 (4); plate M2406 and plate M2364 (4).)|32|.01 P
&(sh)R||||||RIVET, countersunk head, 7/16″ x 1″.  (For plate M1904A and strip M1904D (4).)|4|.01 P
&(sh)R||||||RIVET, countersunk head, 7/16″ x 1⅝″.  (For angle M2075 plate M2073 and strip~   M2074 (6); plate M2389 through 2 hinges M2403 (4).)|10|.01 P
&(sh)R||||||RIVET, countersunk head, 7/16″ x 2¼″.  (For angle M2015A angle M2075 plate~   M2073 and piece M2076 (1); angle M2015B angle M2075 plate M2073 and piece~   M2076 (1).)|2|.01 P
&(sh)R||||||RIVET, countersunk head, ½″ x 1″.  (For plate M989 through plate M993 (1).)|1|.01 P
&(sh)R||||||RIVET, countersunk head, 11/16″ x 1⅜″.  (For plate M2756B channel M2776 (3);~   plate M2756A and channel M2775 (3).)|6|.01 P
&(sh)R||||||RIVET, countersunk head, 11/16″ x 1½″.  (For channel M2143 and plate M2137 (7);~   plate M2757A and strap M2786A (1); plate M2757B and strap M2786B (1); plate~   M3777 and angle M3788 (1); plate M3778 and angle M3800 (1).)|11|.01 P''')

r=add(192,'''&(sh)R||||||RIVET, countersunk head, 11/16″ x 1⅝″.  (For plate M2732A and strap M2784A (1);~   plate M2732B and strap M2784B (1); plate M2740A and strap M2784A (1); plate~   M2740B and strap M2784B (1).)|4|$0.01 P
&(sh)R||||||RIVET, countersunk head, 11/16″ x 1¾″.  (For plate M2740A and strip M2812A (2);~   plate M2740B and strip M2812B (2); plate M2740A and strip M2811 (3); plate~   M2740B and strip M2811 (3).)|10|.01 P
&(sh)R||||||RIVET, countersunk head, 11/16″ x 1⅞″.  (For strap M1994B plate M1985 and angle~   M2008B (1); strap M1994A plate M1985 and angle M2008A (1).)|2|.01 P
&(sh)R||||||RIVET, countersunk head, 11/16″ x 2″.  (For strap M1994B strip M2002 and angle~   M2007B (1); strap M1994A strip M2002 and angle M2007A (1).)|2|.01 P
&(sh)R||||||RIVET, countersunk head, copper, 3/16″ x ¼″.  (For spring SH434D (2).)|66|.01 P
&(sh)R||||||RIVET, countersunk head, copper, 3/16″ x ½″.  (For lining M4159 (14).)|14|.01 P
&(sh)R||||||RIVET, countersunk head, copper, 3/16″ x 11/16″.  (For lining SH997C (43).)|43|.01 P
&(sh)R||||||RIVET, countersunk head, copper, ¼″ x ¾″.  (For lining M359 (1).)|2|.01 P
&(sh)R||||||RIVET, countersunk head, copper, ¼″ x 1″.  (For lining M364 (4); lining MX109~   (11).)|30|.01 P
&(sh)R||||||RIVET, countersunk head, copper, ¼″ x 1⅛″.  (For lining MX107 (18); lining~   MX108 (16).)|136|.01 P
&(sh)R||||||RIVET, countersunk head, copper, ¼″ x 1¼″.  (For lining M364 (1).)|2|.01 P
&(sh)R||||||RIVET, countersunk head, copper, ¼″ x 1⅜″.  (For lining MX107 (5); lining~   MX108 (6).)|44|.01 P
(cp)&|||||A6942|RIVET, eye, standard chain.  (For chain JB5D (1); chain JB5C (1).)|7|.20 P
&|||||SH574L|RIVET, platform ammunition storage locking strip|1|.12
&||||X255|803|RIVET, semaphore stirrup ring|2|.38
&||||X319|803|RIVET, semaphore tube|1|.52
&(sh)R||||||RIVET, wagon box, ⅛″ x ½″.  (For hinge SH373L (3); hinge SH373K (3).)|6|.01 P''')
assembly(r,'ROD, clutch, center, length 93″, assembly','7.97',note='&')
component(r,'*one SH229A clutch ROD, center, length 93″ (1)',price='7.89')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')

r=start(193)
assembly(r,'ROD, clutch connecting, front (length 12⅝″), assembly','1.28',note='&')
component(r,'*one M789B clutch connecting ROD, front (1)',ident='—',plate='6',ord='216',price='1.20')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
assembly(r,'ROD, clutch, rear, assembly','3.58',note='&')
component(r,'*one M581 clutch ROD, rear (1)',ident='—',plate='6',ord='218',price='3.50')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
assembly(r,'ROD, clutch throwout auxiliary, rear, assembly','.96',note='&')
component(r,'*one SH953D clutch throwout auxiliary ROD, rear (1)',price='.88')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
assembly(r,'ROD, clutch throwout stop, assembly','1.54',note='&')
component(r,'*one M4151 clutch throwout stop ROD (1)',ord='955',price='1.38')
component(r,' four SH955D clutch throwout stop rod NUT (¾″, ½″ thick).)')
assembly(r,'ROD, connecting, forked end, assembly','28.18',note='&',ident='13440',plate='18',qty='(6)')
component(r,' four (LQ125A) connecting forked end rod BOLT, assembly,')
component(r,'*two —           connecting forked end rod CAP, assembly',price='2.62')
component(r,'*one LQ123A connecting ROD, forked end (6)',mfr='C13226',price='18.50')
pieces(r,''' one LQ136A connecting rod piston pin BUSHING,
 one LQ128A connecting rod crank shaft BEARING, lower half,
 one LQ127A connecting rod crank shaft BEARING, upper half.)''')
assembly(r,'ROD, connecting, plain end, assembly','17.90',note='&',ident='13441',plate='18',qty='(6)')
component(r,' two (LQ133A) connecting plain end rod BOLT, assembly,')
component(r,'*one LQ131B connecting plain end rod CAP',price='2.60')
component(r,'*one LQ131A connecting ROD, plain end (6)',mfr='C13225',price='14.60')
component(r,' one LQ136A connecting rod piston pin BUSHING.)')
assembly(r,'ROD, connecting, assembly','46.08',note='&',ident='—',plate='18',qty='(6)')
pieces(r,''' one — connecting ROD, forked end, assembly,
 one — connecting ROD, plain end, assembly.)''')
assembly(r,'ROD, control, front, assembly','5.58',note='&',qty='(5)')
component(r,'*one M576 control ROD, front (5)',ident='—',plate='6',ord='229',price='5.50')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.\n                For high speed (2); foot brake (2); clutch (1).)')

r=start(194)
assembly(r,'ROD, distributor control connecting, assembly','$1.35',note='&',ident='8333',plate='15')
component(r,' one LQ318A adjustable CLEVIS, S. A. E., ¼″, round head, threaded,')
component(r,'*one LQ315A distributor control connecting ROD (1)',mfr='B8469',price='.10')
component(r,'*one LQ317A rod END, ¼″',mfr='8472',price='.06')
component(r,' one (A8035) rod end PIN, ¼″ x 51/64″, assembly,')
component(r,'*one LQ65F   CLEVIS, male',price='.51')
pieces(r,''' two —         NAIL, wire, 2d,
 one LQ319A NUT, special jam.)''')
assembly(r,'ROD, engine control, assembly','.90',note='&')
component(r,'*one SH993A engine control ROD (1)',ident='—',plate='12',price='.88')
component(r,' one —         NUT, plain, S. A. E., hexagon, 5/16″.)')
assembly(r,'ROD, foot brake, center, assembly','5.17',note='&',qty='(2)')
component(r,'*one M579 foot brake ROD, center (2)',ident='—',plate='6',ord='218',price='5.09')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
assembly(r,'ROD, foot brake, rear, assembly','5.58',note='&',qty='(2)')
component(r,'*one M578 foot brake ROD, rear (2)',ident='—',plate='6',ord='218',price='5.50')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
assembly(r,'ROD, foot brake connecting, rear, assembly','1.03',note='&',qty='(2)')
component(r,'*one SH946D foot brake connecting ROD, rear (2)',ord='946',price='.95')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
assembly(r,'ROD, front control connecting, assembly','1.08',note='&',ident='36',plate='2',qty='(3)')
component(r,'*one M789A front control connecting ROD (length 10⅝″)',ident='—',plate='6',ord='216',price='1.00')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
entry(r,'ROD, governor control spring',note='&',ident='—',plate='12',ord='SH993F',qty='1',price='.68')

r=start(195)
assembly(r,'ROD, high and low speed control lever trigger, assembly','.73',note='&',qty='(2)')
component(r,'*one M743 high and low speed control lever trigger ROD (2)',ident='—',plate='6',ord='224',price='.72')
component(r,' one —     NUT, plain, U. S. Std., hexagon, ¼″.)')
assembly(r,'ROD, high speed, brake, rear, assembly','12.43',note='&',qty='(2)')
component(r,'*one M575 high speed brake ROD, rear (2)',ident='—',plate='6',ord='229',price='12.35')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
assembly(r,'ROD, low speed brake, front (length 49½″), assembly','5.16',note='&',qty='(2)')
component(r,'*one M574 low speed brake ROD front (2)',ident='—',plate='6',ord='229',price='5.08')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
assembly(r,'ROD, low speed brake, rear, assembly','10.43',note='&',qty='(2)')
component(r,'*one M573 low speed brake ROD, rear (2)',ident='—',plate='6',ord='229',price='10.35')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
assembly(r,'ROD, low speed brake connecting, assembly','.66',note='&',qty='(2)')
component(r,'*one SH946E low speed brake connecting ROD (2)',price='.58')
component(r,' two —     NUT, plain, U. S. Std., hexagon, ¾″.)')
assembly(r,'ROD, reverse operating lever trigger, assembly','.79',note='&')
component(r,'*one M778 reverse operating lever trigger ROD (1)',ord='211',price='.78')
component(r,' one —     NUT, plain, U. S. Std., hexagon, ¼″.)')
assembly(r,'ROD, reversing, center, assembly','2.00',note='&')
component(r,'*one M566 reversing ROD, center (1)',ident='—',plate='6',ord='218',price='1.92')
component(r,' two —     NUT, pipe lock, ¾″.)')
assembly(r,'ROD, reversing, front, assembly','1.06',note='&')
component(r,'*one M571 reversing ROD, front (1)',ident='—',plate='6',ord='230',price='.98')
component(r,' two —     NUT, pipe lock, ¾″.)')
entry(r,'ROD, reversing, rear',note='&',brit='M565',ord='230',qty='1',price='4.75')
assembly(r,'ROD, spark control, length 24″, assembly','.62',note='&')
component(r,'*one SH968D spark control ROD, length 24″ (1)',ident='—',plate='12',price='.58')
component(r,' two —     NUT, plain, S. A. E., hexagon, ⅜″.)')

r=start(196)
assembly(r,'ROD, spark control, over all length 7″, assembly','$0.50',note='&')
component(r,'*one SH968H spark control ROD, over all length 7″ (1)',ident='—',plate='12',price='.48')
component(r,' one —     NUT, plain, S. A. E., 5/16″.)')
assembly(r,'ROD, (spark) control, over all length 92½″, assembly','2.04',note='&')
component(r,'*one SH969C (spark) control ROD, over all length 92½″ (1)',price='2.00')
component(r,' two —     NUT, plain, S. A. E., hexagon, ½″.)')
assembly(r,'ROD, spark and throttle control, over all length 21½″ (vertical), assembly','.52',note='&',qty='(2)')
component(r,'*one SH969D spark and throttle control ROD, over all length 21½″ (2)',price='.48')
component(r,' two —     NUT, plain, S. A. E., hexagon, ½″.)')
assembly(r,'ROD, spark and throttle control, over all length 60½″, assembly','1.39',note='&',qty='(2)')
component(r,'*one SH969A spark and throttle control ROD, over all length 60½″ (2)',price='1.35')
component(r,' two —     NUT, plain, S. A. E., hexagon, ½″.)')
assembly(r,'ROD, throttle control, over all length 22½″, assembly','.97',note='&')
component(r,'*one SH993K throttle control ROD, over all length 22½″ (1)',ident='—',plate='12',price='.95')
component(r,' one —     NUT, plain, S. A. E., hexagon, ⅜″.)')
assembly(r,'ROD, throttle control, length 51¾″, assembly','1.19',note='&')
component(r,'*one SH968A throttle control ROD, length 51¾″ (1)',ident='—',plate='12',price='1.15')
component(r,' two —     NUT, plain, S. A. E., hexagon, ⅜″.)')
assembly(r,'ROD, throttle control, over all length 91″, assembly','2.04',note='&')
component(r,'*one SH969B throttle control ROD, over all length 91″ (1)',price='2.00')
component(r,' two —     NUT, plain, S. A. E., hexagon, ½″.)')
append_rows(r,'''&|||8082||LQ64A|ROLLER, cam shaft rocker lever|24|.33
&||||M2148|362|ROLLER, sliding door|4|.69''')

r=add(197,'''X|—|29||M2848|478|ROLLER, sponson shaft|2|1.58''')
assembly(r,'ROLLER, track, with flange, assembly','70.20',note='%(gp)X',ident='15',plate='2',qty='(gp) (28)')
pieces(r,''' one —       track ROLLER, assembly,
 one M1336 track roller SPRING,''')
component(r,'*two M1334 track roller spring PLATE (56)',ident='2',plate='29',ord='59',price='6.50')
entry(r,'ROLLER, track, assembly',note='%(gp)X',qty='(gp) (58)',price='52.20');stacked(r,ident='—\n14',plate='29\n2');composed(r)
component(r,'*two M1332 track ROLLER (116)',ident='6',plate='29',ord='56',price='8.25')
component(r,' two M1335 track roller spring split RING,')
component(r,'*one M1333 track roller TUBE (58).)',ident='5',plate='29',ord='57',price='35.00')
entry(r,'ROLLER, track roller pinion',note='%X',ident='2',plate='25',brit='M1542',ord='53',qty='36',price='.85')
assembly(r,'ROTOR, distributor, assembly','.49 P',note='%X',mfr='D13720',qty='(2)')
pieces(r,'''*one D13691 distributor ROTOR (2),
 one D29616 distributor rotor attaching SCREW,
 one D14182 distributor rotor BRUSH, with spring, assembly,
*one D29621 distributor rotor high tension CONNECTOR,
 one D30060 WASHER, lock, .195″ x .453″ x .046″,
 one D25116 WASHER, plain, .147″ x .313″ x .022″.)''')
append_rows(r,'''%X||||M996|501|SADDLE, louvre|4|.68
&|||8366||LQ235A|SCREEN, crank case breather|1|.02''')
assembly(r,'SCREEN, crank case oil filler, assembly','.15',note='%X',qty='(2)')
component(r,'*one LQ226A crank case oil filler SCREEN (2)',mfr='8521',price='.10')
component(r,'*one LQ227A crank case oil filler screen RING (2).)',mfr='8522',price='.05')
append_rows(r,'''&|||8528||LQ204A|SCREEN, crank case oil sump oil strainer, side|1|.15
&|||8529||LQ205A|SCREEN, crank case oil sump oil strainer, top|1|.15
&|||8533||LQ451A|SCREEN, oil pump, side|2|.50
&|||B8465||LQ452A|SCREEN, oil pump lower, top|1|.50
&|||8532||LQ457A|SCREEN, oil pump upper, top|1|.50''')
assembly(r,'SCREW, airplane watch mat, assembly','.04 P',note='%X',qty='(4)')
pieces(r,''' one —          NUT, machine screw, No. 8 (5/32″)—30,
*one —          SCREW, machine, round head, No. 8 (5/32″)—30 x 1⅜″ (4),
 two SH979E WASHER, plain, I. D. .18″, O. D. ½″, thick .05″.)''')
append_rows(r,'''%X|||H/20793||637|SCREW, (ball mount) splash ring|2|.08
&|||B8108||LQ33A|SCREW, cam shaft bearing lock|14|.30''')

r=add(198,'''%(sh)R||||||SCREW, cap, fillister head, ⅜″ x ½″.  (For bracket SH994D (2); bracket SH994E~   (2).)|4|$0.03 P
&(sh)R||||||SCREW, cap, U. S. Std., flat head, ⅛″ x ½″.  (For ring SH861E (2).)|2|.02 P
&(sh)R||||||SCREW, cap, U. S. Std., flat head, 3/16″ x ⅝″.  (For disk X267 (4).)|4|.03 P
&(sh)R||||||SCREW, cap, U. S. Std., flat head, ¼″ x ¾″.  (For container LQ392A (1).)|1|.03 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, ¼″ x 1″.  (For rest SH573K (3).)|3|.03 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, 5/16″ x ¾″.  (For box SH373A (2).)|2|.03 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, 5/16″ x ⅞″, with plain nut and lock washer.~   (For fastener SH445E (1).)|(1)|.05 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, 5/16″ x 1″, with plain nut and lock washer.~   (For channel SH485E (6); angle SH485B (6).)|(18)|.05 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, ⅜″ x ½″.  (For plate SH608B (4).)|4|.06 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, ⅜″ x 1⅛″, with plain nut and lock washer.~   (For plate M2065 (10); plate SH575A (4).)|(24)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, ⅜″ x 1 5/16″, with plain nut and plain washer.~   (For rest M2842 (3).)|(6)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, ⅜″ x 1½″, with plain nut and lock washer.~   (For water can bracket, inner, assembly (2); outer, (assembly (2).)|(4)|.06 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, ½″ x 1″.  (For plate M2034 (4).)|12|.05 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, ⅝″ x 1½″, with plain nut and lock washer.~   (For plate M1004 (4).)|(16)|.06 P
%(sh)R||||||SCREW, cap, U. S. Std., flat head, ⅝″ x 1¾″, with plain nut and lock washer.~   (For handle M3131 (1); angle M2792B (4); angle M2792A (4).)|(14)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flathead, ⅝″ x 1⅞″, with plain nut and lock washer.~   (For angle M2792B (2); M2792A (2).)|(4)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flathead, ⅝″ x 2⅛″, with plain nut and lock washer.~   (For plate M2800 (7); plate M2802 (7); angle M2791B (3); M2791A (3); angle~   M2792B (2); M2792A (2).)|(24)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flathead, ⅝″ x 2 3/16″, with plain nut and lock washer.~   (For plate M2799 (7).)|(7)|.07 P''')

r=add(199,'''%(sh)R||||||SCREW, cap, U. S. Std., flathead, ⅝″ x 2¼″, with plain nut and lock washer.~   (For hinge M2826 (1).)|(4)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flathead, ⅝″ x 2⅜″, with plain nut and lock washer.~   (For hinge M2826 (1).)|(4)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flathead, ⅝″ x 2½″, with plain nut and lock washer.~   (For hinge M2826 (1).)|(4)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flathead, ⅝″ x 2⅝″, with plain nut and lock washer.~   (For angle M2791B (1); M2791A (1).)|(2)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flathead, ⅝″ x 2⅞″, with plain nut and lock washer.~   (For angle M2791B (1); angle M2791A (1).)|(2)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flathead, ⅝″ x 3½″, with plain nut and lock washer.~   (For hinge M2826 (1).)|(4)|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., flathead, ⅝″ x 3⅝″, with plain nut and lock washer.~   (For angle M2792B (1); M2792A (1).)|(2)|.08 P
%(sh)R||||||SCREW, cap, U. S. Std., flathead, ¾″ x 3 9/16″, with plain nut and lock washer.~   (For bracket M2382 (1).)|(2)|.08 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ¼″ x 7/16″.  (For guide M2155A (7);~   guide M2155B (7); guide M2208 (6).)|20|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ¼″ x ½″.  (For cover SH146B (4); plate~   M1126 (4).)|12|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ¼″ x ⅝″.  (For fastener SH445H (2);~   guide M2156 (9).)|11|.02 P
%X|||||SH424E|SCREW, cap, U. S. Std., hexagon head, ¼″ x ¾″, slotted head.  (For four clips~   M2437 (2).)|8|.03 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ¼″ x ⅞″, drilled head.  (For plate M1047~   (4).)|4|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, 5/16″ x ⅜″.  (For guide M2165 (8); guide~   M2166 (6).)|22|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, 5/16″ x ½″.  (For holder SH443A (2).)|2|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, 5/16″ x ⅝″.  (For securing bracket M2170~   (6).)|6|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, 5/16″ x ¾″.  (For cylinder SH900C (2);~   securing funnel rack, assembly (1).)|9|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, 5/16″ x ⅞″.  (For cover SH399A (4).)|4|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, 5/16″ x 2½″.  (For cover SH399A (2).)|2|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅜″ x ½″.  (For plate SH608A (4);~   bracket SH980D (2); bracket B5924 (2); bracket B5929 (2); bracket B5926 (2);~   securing accessories or ration box (7); support B5930 (2).)|30|.03 P''')

r=add(200,'''%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅜″ x ⅝″.  (For plate M880 (4); plate~   M995A (9); plate M995B (9); flange SH951B (8).)|50|$0.03 P
%(sh)R|13|21||||SCREW, cap, U. S. Std., hexagon head, drilled, ⅜″ x ⅝″.  (For collar SH999A~   (6).)|6|.04 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅜″ x ¾″.  (For generator (3); catch~   M2153 (1); bearing SH900A (3); plate M1033 (19); plate M1035A (8); cover M1038~   (8); securing duct M1036 (between radiator and roof) (23); securing pyrene refill~   bracket, assembly (3).)|72|.03 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅜″ x 1″.  (For strip SH978T (1); bracket~   SH971A (2); bracket SH971B (2); brace SH920F (2); bracket SH293B (1); bracket~   SH293A (1); cover M1124 (2).)|11|.03 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅜″ x 1 5/16″.  (For bracket M1048 (2).)|2|.03 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅜″ x 1½″.  (For cover M1124 (2).)|2|.04 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ½″ x ½″.  (For housing SH957A (4).)|4|.05 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ½″ x ⅝″.  (For holder SH959B (4).)|4|.05 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ½″ x ¾″.  (For plate M1411 (1).)|4|.05 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ½″ x ⅞″.  (For flange B40B (6).)|18|.05 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ½″ x 1″.  (For cone SH959A (1); connec-~   tion M1231 (3).)|4|.05 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ½″ x 1¼″.  (For cradle B39A (2).)|10|.06 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ½″ x 1½″.  (For bracket M184 (2).)|2|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ½″ x 1¾″.  (For bracket M4148 (4).)|4|.07 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ½″ x 2″.  (For bracket M639 (2).)|6|.08 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅝″ x ¾″.  (For tank M1193 (2).)|2|.09 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅝″ x ⅞″.  (For angle M2087 (3); angle~   M2088 (4).)|14|.09 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅝″ x 1″.  (For tee SH975A (3); connec-~   tion M1231 (3); socket M1230 (3); flange B/20793 through A/20793 (12).)|21|.09 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅝″ x 1¼″.  (For rail M2009B (5); rail~   M2009A (6); rail (outer) M2011B (2); rail (outer) M2011A (2); rail (inner) M2011B||''')

r=add(201,'''||||||   (15); rail (inner) M2011A (15); rail (inner) 2010M B (15); rail (inner) M2010A (15);~   rail M2012B (15); rail M2012A (15); rail (inner) M2013B (14); rail (inner) M2013A~   (14); rail (outer) M2013B (12); rail (outer) M2013A (12).)|196|.10 P
%X|1|21|||SH866B|SCREW, cap, U. S. Std., hexagon head, ⅝″ x 1¼″, threaded 1″, drilled head.~   (For securing clutch drum to flywheel.)|6|.11
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅝″ x 1⅞″.  (For bracket SH953A (4).)|4|.10 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅝″ x 2″.  (For rail M2009B through hook~   (2); rail M2009A through hook (2); rail M2011B (outer) (13); rail M2011A (outer)~   (13); rail M2010B (outer) (15); rail M2010A (outer) (15); rail M2013B (outer)~   through towing carrying cable (2); rail M2013A (outer) through towing carrying~   cable (2).)|68|.13 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ⅝″ x 2¼″.  (For securing box M1123 to~   floor (4).)|4|.13 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ¾″ x 1⅝″.  (For angle M2089 (7).)|14|.15 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ¾″ x 1¾″.  (For bracket M1472 (4).)|16|.15 P
%(sh)R||||||SCREW, cap, U. S. Std., hexagon head, ¾″ x 2¼″.  (For bearing M1407 (6).)|24|.16 P
%(sh)R||||||SCREW, cap, U. S. Std., round head, 3/16″ x ½″.  (For stirrup X253 (2); sleeve~   M4023 (1).)|3|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., round head, ¼″ x ⅜″.  (For bracket SH373N (2); spring~   SH395K (2).)|6|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., round head, ¼″ x 7/16″.  (For holder SH285A (2).)|2|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., round head, ¼″ x ½″.  (For switch C67 (4); switch C65~   (4); switch C64 (4); switch C66 (4); clip A264 (1); clip A263 (1); switch (3).)|49|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., round head, ¼″ x ⅝″.  (For four clips M2437 (2).)|8|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., round head, ¼″ x 2″, with plain nut, lock and plain~   washer.  (For switch C5261 (2).)|(2)|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., round head, 5/16″ x 1″, with two plain nuts and lock~   washer.  (For starting motor, to battery negative terminal cover cable; starting~   motor, to starting switch cable; starting switch, to starting battery positive ter-~   minal cover cable terminal B7028J (1).)|(3)|.02 P
%(sh)R||||||SCREW, cap, U. S. Std., round head, ⅜″ x 9/16″.  (For clip SH372C (2); (three)~   clips SH372A (2).)|14|.03 P
%(sh)R||||||SCREW, cap, U. S. Std., round head, ⅜″ x ⅝″.  (For (one) clip SH372A (2).)|2|.03 P
%(sh)R||||||SCREW, cap, U. S. Std., round head, 7/16″ x 1¼″, with plain nut and lock washer.~   (For cover plate M2424 (1).)|(1)|.05 P
&|||255||LQ510A|SCREW, carburetor (U. S. Std., ¼″ x 7/16″ under head, drilled)|8|.03
&|||13364||LQ515A|SCREW, carburetor altitude air valve stop|4|.04
&|||13370||LQ522A|SCREW, carburetor butterfly set|12|.02''')

r=start(202)
assembly(r,'SCREW, carburetor channel, assembly','$0.03',note='&',qty='(4)')
component(r,'*one LQ525A carburetor channel SCREW (4)',mfr='13376',price='.02')
component(r,' one LQ527A carburetor channel screw WASHER.)')
append_rows(r,'''&|||13293||LQ540A|SCREW, carburetor gear sector adjusting|2|.09
&|||253||LQ508A|SCREW, carburetor (gear sector adjusting screw clamping)|2|.01
&|||13538||LQ558A|SCREW, carburetor gear sector set|4|.03
&|||13405||LQ564A|SCREW, carburetor priming plug|12|.02
&|||13416||LQ557A|SCREW, carburetor throttle shaft end (machine screw, No. 10 x 7/16″ drilled)|8|.05
&|||B12429||LQ420A|SCREW, carburetor to intake header, long|1|.15
&|||B13152||LQ419A|SCREW, carburetor to intake header, short|1|.12
&|||||SH861H|SCREW (clutch sliding collar), key|8|''')
assembly(r,'SCREW, clutch throwout lever pin locking set, assembly','.10',note='%X',qty='(2)')
component(r,'*one M4175 clutch throwout lever pin locking set SCREW (2)',ord='955',price='.08')
component(r,' one —     NUT, plain, U. S. Std., hexagon, 7/16″.)')
entry(r,'SCREW, crank shaft thrust bearing retaining nut lock',note='&',ident='8520',plate='14',mfr='8520',ord='LQ276A',qty='1',price='.04')
assembly(r,'SCREW, distributor contact, assembly','.38 P',note='%X',qty='(6)')
pieces(r,'''*one D13687 distributor contact SCREW (6),
 one D21748 NUT, plain, No. 5—50 x 7/32″ x 7/64″ thick.)''')
assembly(r,'SCREW, distributor contact arm spring, assembly','.07 P',note='&',qty='(4)')
pieces(r,''' one D29573 NUT, castle, No. 6—32 x .218″ x .188″ thick,
 one D30816 PIN, wire, .031″ x .625″,
*one D29574 SCREW, hexagon head, No. 2—36 x .345″,
 one D29576 WASHER, plain, .144″ x .469″ x .022″.)''')
append_rows(r,'''&|||D29574|||SCREW, distributor contact arm spring|4|.02 P
%X|||D29616|||SCREW, distributor rotor|2|.03 P''')

r=start(203)
assembly(r,'SCREW, distributor terminal nut, assembly','.07 P',note='&',qty='(4)')
pieces(r,'''*one D31012 distributor terminal nut SCREW (4),
 one D30996 distributor terminal screw NUT (round, brass, No. 10—35~                   x .360″ x .171″ thick).)''')
append_rows(r,'''&|||||SH142B|SCREW, governor arm bushing set|1|.12
&|||||SH65A|SCREW, hand starter (machine, A. S. M. E., No. 10, drilled head)|4|.09
&|||||SH428A|SCREW, hemispherical turret|18|.08
&|||D30620|||SCREW, ignition switch ammeter terminal connector|1|.03 P
&|||D30169|||SCREW, ignition switch cover plate|2|.02 P
&|||D30168|||SCREW, ignition switch cover plate (center)|1|.04 P
&|||D23745|||SCREW, ignition switch lever|2|.02 P''')
assembly(r,'SCREW, ignition switch resistance unit, assembly','.10 P',note='&',qty='(2)')
component(r,'*one D30362 ignition switch resistance unit SCREW',price='.07')
pieces(r,''' one D29864 NUT, castle, No. 10—30 x .437″ x .218″ thick,
 one —     PIN, split, brass, 1/16″ x ⅝″.)''')
append_rows(r,'''&|||||SH81H|SCREW, key|8|.04
&||||M3127|428|SCREW, locking.  (For bracket M3121 (1); hemispherical turret, assembly (3).)|9|.08
&(sh)R||||||SCREW, machine, flathead, No. 10 (3/16″)—24 x ¾″.  (For key SH136B (1).)|1|.01 P
&(sh)R||||||SCREW, machine, flathead, No. 14 (¼″)—20 x ¾″, brass.  (For band M360 (1).)|2|.01 P
&(sh)R||||||SCREW, machine, headless, No. 7 (5/32″)—32 x ¼″.  (For header SH103A (1).)|6|.01 P
&(sh)R||||||SCREW, machine, round head, No. 8 (5/32″)—30 x 3/16″.  (For hood SH105D (2).)|2|.01 P
&(sh)R||||||SCREW, machine, round head, No. 8 (5/32″)—30 x 5/16″.  (For cover SH105A (12).)|12|.01 P
&(sh)R||||||SCREW, machine, round head, No. 8 (5/32″)—30 x ⅜″.  (For box SH102C (6).)|6|.01 P
&(sh)R||||||SCREW, machine, round head, No. 8 (5/32″)—30 x ⅜″, with machine screw nut.~   (For tachometer (4).)|(4)|.01 P
&(sh)R||||||SCREW, machine, round head, No. 8 (5/32″)—30 x 1″, with machine screw nut and~   plain washer.  (For switch C5261 (2).)|(6)|.01 P
&(sh)R||||||SCREW, machine, round head, brass, No. 8 (5/32″)—32 x 7/16″.  (For unilet, type~   T (2).)|2|.01 P
%(sh)R||||||SCREW, machine, round head, No. 10 (3/16″)—32 x ⅜″.  (For clip SH373M (2).)|2|.01 P
&(sh)R||||||SCREW, machine, round head, No. 10 (3/16″)—24 x ¼″.  (For tube SH101B (1).)|6|.01 P
&(sh)R||||||SCREW, machine, round head, brass, No. 10 (3/16″)—24 x ¼″.  (For header~   SH103A (1).)|6|.01 P
&(sh)R||||||SCREW, machine, round head, No. 10 (3/16″)—24 x 5/16″.  (For securing Liberty~   Ordnance engine name plate to upper crank case (4).)|4|.01 P
&(sh)R||||||SCREW, machine, round head, No. 10 (3/16″)—24 x ⅜″ brass.  (For terminal~   LQ380A (1); terminal LQ381A (1).)|2|.01 P''')

r=add(204,'''%(sh)R||||||SCREW, machine, round head, brass, No. 10 (3/16″)—32 x ⅜″.  (For unilet, type~   L (2).)|(2)|$0.01 P
%(sh)R||||||SCREW, machine, round head, No. 10 (3/16″)—24 x ½″, with machine screw nut~   and lock washer.  (For support SH585B (2).)|(2)|.03 P
%(sh)R||||||SCREW, machine, round head, No. 10 (3/16″)—24 x ¾″, with machine screw nut,~   plain washer and lock washer.  (For support SH962A (2).)|(2)|.01 P
%(sh)R||||||SCREW, machine, round head, No. 10 (3/16″)—24 x 1″, with machine screw nut and~   lock washer.  (For distance recorder (3).)|(3)|.01 P
%(sh)R||||||SCREW, machine, round head, No. 14 (¼″)—20 x ½″.  (For cover SH281A (4);~   plate SH281C (4).)|8|.01 P
%X|||||SH574G|SCREW, platform ammunition storage (locking strip) thumb|1|
%X|||||SH801B|SCREW, semaphore locking|1|
&(sh)R||||||SCREW, set, headless, 5/16″ x ½″.  (For bushing M261 (1).)|2|.02 P
%(sh)R||||||SCREW, set, square head, cone point, ⅜″ x ¾″.  (For bracket M2382 (1).)|2|.02 P
&(sh)R||||||SCREW, set, square head, cup point, ¼″ x ¼″.  (For collar SH101F (1).)|2|.01 P
&(sh)R||||||SCREW, set, square head, cup point, ¼″ x ⅜″.  (For collar SH102K (1).)||.01 P
%(sh)R||||||SCREW, set, square head, cup point, ¼″ x ⅝″.  (For pulley SH102A (1); con-~   nection SH964G (1).)|3|.01 P
%(sh)R||||||SCREW, set, square head, cup point, 5/16″ x 1″.  (For fan SH960A (2).)|2|.01 P
%(sh)R||||||SCREW, set, square head, cup point, ½″ x 2″, with plain nut.  (For plate M982~   (2); plate M989 (2).)|(4)|.08 P
%(sh)R||||||SCREW, set, square head, cup point, ⅝″ x ⅞″.  (For lever M4162 (1).)|1|.06 P
%(sh)R||||||SCREW, set, square head, round point, ⅛″ x ⅜″.  (For holder SH950H (1).)|1|.01 P
&|||D30108|||SCREW, slotted head, No. 2—64 x .215″.  (For voltage regulator, assembly D5718~   (2).)|2|.01 P
&|||D26948|||SCREW, slotted head, No. 6—38 x ¼″.  (For ignition switch, assembly D1120 (1).)|1|.10 P
&|||D29598|||SCREW, slotted head, No. 8—32 x .391″.  (For distributor cup, assembly D14180~   (2).)|4|.01 P
&|||D25673|||SCREW, slotted head, 5/16″—24 x .562″|8|.01 P
&|||B215||LQ418A|SCREW, special 5/16″ x 11/16″.  (For elbow LQ308A (2).)|24|.37''')
