import pandas as pd

projects = pd.read_csv("projects.csv", sep=";")
history = pd.read_csv("projects_history.csv", sep=";")
report = pd.read_csv("report.csv", sep=";")
changes = pd.read_csv("service_changes.csv", sep=";")
terms = pd.read_csv("service_terms.csv", sep=";")
works = pd.read_csv("works.csv", sep=";")

works["month"] = pd.to_datetime(works["month"])
report["report_generated_at"] = pd.to_datetime(report["report_generated_at"])

# 1) Logical clients after project-id replacements
all_ids = set(projects["project_id"])
replacement_ids = set(history["new_project_id"])
logical_roots = all_ids - replacement_ids
print("Logical clients:", len(logical_roots))
print("Unique client_id in report:", report["client_id"].nunique())

# 2) Rows newer than the report
cutoff = report["report_generated_at"].max()
print("\nWorks newer than report:")
print(works[works["month"] > cutoff].sort_values(["project_id", "month"]))

# 3) Split payments: aggregate activity at project-month level
monthly = (works.groupby(["project_id", "month"], as_index=False)
          .agg(amount=("amount", "sum"),
               rows=("amount", "size")))
print("\nProject-months represented by several source rows:")
print(monthly[monthly["rows"] > 1])

# 4) Service changes
print("\nService changes:")
print(changes)

# 5) Project-id overlaps around renames
for _, h in history.iterrows():
    old_id, new_id = h["project_id"], h["new_project_id"]
    old_months = set(works.loc[works.project_id == old_id, "month"])
    new_months = set(works.loc[works.project_id == new_id, "month"])
    print(f"Overlap {old_id}->{new_id}:", sorted(old_months & new_months))

# 6) STOP followed by positive activity
stop_rows = works[works["label"].fillna("").str.lower() == "стоп"]
for _, r in stop_rows.iterrows():
    later = works[(works.project_id == r.project_id) &
                  (works.month > r.month) &
                  (works.amount > 0)]
    if not later.empty:
        print(f"STOP followed by activity for {r.project_id}:")
        print(later[["month", "amount"]])

# Final corrected report is stored in report_fixed.csv.
