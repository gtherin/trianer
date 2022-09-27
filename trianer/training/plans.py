"""
80: course rapide
70-75: course normale
65-70: aisance respiratoire, peux parler pendant la course
sl is slow run, trotinant
    """

# https://www.kalenji.fr/terminer-mon-premier-marathon-en-12-semaines
training_plan_marathon = (
    ["l:w1", "f:1h,hr:70-75", "f:1h,hr:70-75", "f:1h30,hr:70-75"]
    + ["l:w2", "f:1h,hr:70-75", "f:1h,hr:65-70+f:0h05,hr:80+f:0h10,hr:60", "f:1h45,hr:65-70"]
    + ["l:w3", "f:1h,hr:70-75", "f:0h55,hr:65-70+f:0h10,hr:80+f:0h10,hr:60", "f:2h,hr:65-70"]
    + ["l:w4", "f:0h45,hr:70-75", "rest", "f:1h,hr:70-75"]  # Rest week
    + ["l:w5", "f:1h30,hr:70-75", "f:h42,hr:65-70+f:0h08,hr:80+f:0h10,hr:60", "f:1h30,hr:65-70"]
    + ["l:w6", "f:1h30,hr:70-75", "f:h30,hr:65-70+f:h8,hr:80+sl:h5+f:h8,hr:80+f:h9,hr:60", "f:1h30,hr:65-70"]
    + ["l:w7", "f:1h30,hr:70-75", "f:25,hr:65-70+f:h10,hr:80+sl:h5+f:h10,hr:80+f:h10,hr:60", "f:2h,hr:65-70"]
    + ["l:w8", "f:1h,hr:70-75", "rest", "f:1h,hr:65-70"]  # Rest week
    + ["l:w9", "f:1h30,hr:70-75", "f:40,hr:65-70+f:h12,hr:80+f:h8,hr:60", "f:2h15,hr:65-70"]
    + [
        "l:w10",
        "f:25,hr:65-70+f:h10,hr:80+sl:h5+f:h10,hr:80+f:h10,hr:60",
        "f:1h15,hr:65-70+f:h5,hr:80+f:h10,hr:60",
        "f:1h30,hr:70-75",
    ]
    + [
        "l:w11",
        "f:1h,hr:70-75",
        "f:26,hr:65-70+f:h5,hr:max+sl:h3+f:h5,hr:max+sl:h3+f:h5,hr:max+sl:h3+f:h10,hr:60",
        "f:1h30,hr:70-75",
    ]
    + ["l:w12", "f:1h,hr:70-75", "rest", "w:h10"]  # Rest week
)

# https://www.schneiderelectricparismarathon.com/fr/se-preparer/plan-guides

# https://www.timeto.com/Assets/TimeTo/plans/marathon_3h00

# https://www.timeto.com/Assets/TimeTo/plans/marathon_4h00
