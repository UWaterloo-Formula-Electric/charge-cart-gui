# Output of "BatteryInfo"

# Note: Index 0: cell_1
# split('\t') -> strip (get rid of white space)
# -> dictionary (70 key-value pairs, unsplitted) -> splitted (a list of 5 dictionary)
BatteryInfoString = """
Index   Cell Voltage(V) Temp Channel(degC)
0       4.061700        23.020077
1       4.014800        22.730888
2       4.014200        23.102329
3       4.013200        22.837366
4       4.015400        23.154150
5       4.014600        22.809973
6       4.018900        22.913471
7       4.030200        22.743057
8       4.026900        22.910419
9       4.027100        22.743057
10      4.026500        23.010914
11      4.027100        22.740007
12      4.027800        22.919577
13      4.030100        22.834318
14      4.036400        22.688293
15      4.025500        22.892170
16      4.024200        22.715673
17      4.024200        22.910419
18      4.024900        22.575800
19      4.027500        22.983500
20      4.027500        22.682199
21      4.028500        22.901291
22      4.027000        22.594025
23      4.027200        22.953060
24      4.027200        22.627483
25      4.035600        22.861713
26      4.028400        22.651806
27      4.030500        22.870838
28      4.026600        22.703510
29      4.024100        22.983500
30      4.023500        22.803902
31      4.022800        23.151093
32      4.024200        22.691343
33      4.027500        23.178537
34      4.027200        22.773460
35      4.027900        23.041393
36      4.026000        22.883013
37      4.026000        22.898243
38      4.026500        22.736958
39      4.026300        22.937828
40      4.027300        22.831297
41      4.028700        22.925648
42      4.028400        22.575800
43      4.027200        22.956114
44      4.025400        22.682199
45      4.022000        22.873892
46      4.026100        22.752172
47      4.028400        23.065765
48      4.028800        22.755222
49      4.030000        22.977423
50      4.028300        22.727839
51      4.027700        22.785631
52      4.027200        22.609230
53      4.028300        22.806953
54      4.028800        22.825195
55      4.030400        22.563644
56      4.026600        22.609230
57      4.024600        22.959135
58      4.024500        22.752172
59      4.024900        23.068821
60      4.024100        22.685246
61      4.027300        22.876944
62      4.027100        22.651806
63      4.027100        22.983500
64      4.026700        22.578848
65      4.026800        22.806953
66      4.026500        22.749123
67      4.026300        22.837366
68      4.027500        22.764343
69      4.029100        22.831297
"""

OtherBattInfo = """
IBUS    VBUS    VBATT
0.050573        -1.800297       -2.447110

MinVoltage      MaxVoltage      MinTemp MaxTemp PackVoltage
4.011531        4.060500        20.949930       21.538898       281.745911

*Note Temp is not related to a specific cell number

"""
