#! /usr/bin/env python3
import pandas as pd

def parse(file_name):
    df = pd.read_csv(file_name)
    label = df.Label.values
    traindf = df.ID.str.rsplit("_", n=1, expand=True)
    traindf.loc[:, "label"] = label
    traindf = traindf.rename({0: "ID", 1: "subtype"}, axis=1)

    types=["subdural","subarachnoid","intraventricular","intraparenchymal","epidural","any"]

    type_labels=[traindf[traindf["subtype"]==x][["ID","label"]].rename({
        "label":x
    },axis=1) for x in types]

    out=type_labels[0]
    for x in type_labels[1:]:
        out=pd.merge(out,x,on="ID")
    return out

if __name__ == "__main__":
    df=parse("test/stage_1_train.csv")
    print(df.head())
