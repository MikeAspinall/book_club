import pandas as pd

def parse_stacked_ratings(df, keep_totals=True):
    records = []
    nrows, ncols = df.shape
    i = 0

    while i < nrows:
        # check for book header in column 0 and empty-ish column 1 (as in your layout)
        first_cell = df.iat[i, 1] if ncols > 0 else None
        second_cell = df.iat[i, 0] if ncols > 1 else None

        if pd.notna(first_cell) and (ncols == 1 or pd.isna(second_cell)):
            heading = str(first_cell).strip()
            if "(" in heading and heading.endswith(")"):
                book, chooser = heading.rsplit("(", 1)
                book = book.strip()
                chooser = chooser[:-1].strip()

                # safe: take the whole next row as Series (this avoids scalar selection)
                if i + 1 >= nrows:
                    break
                reviewers_row = df.iloc[i + 1]

                # find reviewer column indices (start at col 1 by layout)
                reviewer_cols = [col for col in reviewers_row.index[1:] if pd.notna(reviewers_row.loc[col])]
                # fallback: if nothing found, take any non-na in the row
                if not reviewer_cols:
                    reviewer_cols = [col for col in reviewers_row.index if pd.notna(reviewers_row.loc[col])]

                reviewers = [str(reviewers_row.loc[col]).strip() for col in reviewer_cols]

                # iterate criteria rows until the next blank first column
                j = i + 2
                while j < nrows and pd.notna(df.iat[j, 0]):
                    criterion = str(df.iat[j, 0]).strip()
                    # optionally skip "Total" rows (they can be recomputed)
                    if not keep_totals and criterion.lower().strip().startswith("total"):
                        j += 1
                        continue

                    for col, reviewer in zip(reviewer_cols, reviewers):
                        # guard if the column index is out of bounds
                        score = df.iat[j, col] if (isinstance(col, int) and col < ncols) else df.loc[j, col]
                        # convert numeric-like values to float where possible
                        if pd.isna(score):
                            score_val = None
                        else:
                            try:
                                score_val = float(score)
                            except Exception:
                                score_val = score
                        records.append({
                            "Book": book,
                            "Chooser": chooser,
                            "Criterion": criterion,
                            "Reviewer": reviewer,
                            "Score": score_val
                        })
                    j += 1

                i = j
            else:
                i += 1
        else:
            i += 1

    return pd.DataFrame(records)