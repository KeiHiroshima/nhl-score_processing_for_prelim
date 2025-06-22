import os

import numpy as np
import pandas as pd


def split_random(df, seed=42):
    # ランダムシードを固定
    np.random.seed(seed)

    # データフレームをランダムに8つのグループに分割
    df_shuffled = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    group_size = len(df) // 8

    groups = []
    for i in range(8):
        start_idx = i * group_size
        end_idx = (
            start_idx + group_size if i < 7 else len(df)
        )  # 最後のグループは残り全て
        group = df_shuffled.iloc[start_idx:end_idx]
        groups.append(group.sort_values(by="audition_number", ascending=True))

    return groups


def split_even(df, seed=42):
    # ランダムシードを固定
    np.random.seed(seed)

    # データフレームをランダムに8つのグループに分割
    # df_shuffled = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    group_size = len(df) // 8

    # 分割パターン2: 上位50％と下位50％の人数が各グループで均等になるように分割
    top_50 = df.head(len(df) // 2)
    bottom_50 = df.tail(len(df) // 2)

    # shuffle
    top_50 = top_50.sample(frac=1, random_state=seed).reset_index(drop=True)
    bottom_50 = bottom_50.sample(frac=1, random_state=seed).reset_index(drop=True)

    # sample 8 groups
    equal_groups = []
    for i in range(8):
        start_idx = i * (group_size // 2)
        end_idx = start_idx + (group_size // 2)
        top_part = top_50.iloc[start_idx:end_idx]
        bottom_part = bottom_50.iloc[start_idx:end_idx]
        equal_group = pd.concat([top_part, bottom_part]).reset_index(drop=True)
        equal_groups.append(equal_group)
        """
        top_part = top_50.sample(group_size // 2, random_state=seed + i).reset_index(
            drop=True
        )
        bottom_part = bottom_50.sample(
            group_size // 2, random_state=seed + i
        ).reset_index(drop=True)
        equal_group = pd.concat([top_part, bottom_part]).reset_index(drop=True)
        equal_groups.append(equal_group)
        """  # equal_group.to_csv(f'equal_group_{i+1}.csv', index=False)
        # print(top_50.shape, bottom_50.shape, equal_group.shape)

    return equal_groups


def main(data_path):
    df = pd.read_csv(os.path.join(data_path, "top5to36.csv"))
    df_sorted = pd.read_csv(os.path.join(data_path, "top5to36_sorted.csv"))
    # print(df.shape)

    # set random seed randomly
    random_seed = np.random.randint(1000)

    split_random(df_sorted, random_seed)
    split_even(df, random_seed)


if __name__ == "__main__":
    data_path = os.getcwd()
    # print(data_path)

    main(os.path.join(data_path, "outputs_from_script"))
