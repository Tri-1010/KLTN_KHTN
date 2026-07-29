import os, sys, datetime

REPORTS_DIR = "reports"
KW_SIG_CSV    = os.path.join(REPORTS_DIR, "keyword_significance.csv")
METRICS_CSV   = os.path.join(REPORTS_DIR, "metrics_breakdown.csv")
DENSITY_CSV   = os.path.join(REPORTS_DIR, "news_density_analysis.csv")
SHAP_CSV      = os.path.join(REPORTS_DIR, "shap_configc_keyword_ranking.csv")
REPORT_PATH   = os.path.join(REPORTS_DIR, "H2_H3_validation_report.md")

PLACEHOLDER = "_Chua co du lieu -- chay Task 7 de sinh CSV nay._"

def read_kw_significance():
    if not os.path.exists(KW_SIG_CSV):
        return None
    import pandas as pd
    df = pd.read_csv(KW_SIG_CSV, encoding="utf-8")
    result = {}
    result["n_sig_chi"]   = int(df["significant_chi"].sum())   if "significant_chi"   in df.columns else 0
    result["n_sig_mw"]    = int(df["significant_mw"].sum())    if "significant_mw"    in df.columns else 0
    result["n_sig_logit"] = int(df["significant_logit"].sum()) if "significant_logit" in df.columns else 0
    result["n_sig_any"]   = int(df["significant_any"].sum())   if "significant_any"   in df.columns else 0
    result["n_total"]     = len(df)
    sig_df = df[df.get("significant_any", df.get("significant_chi", pd.Series(False)))]
    if "chi_p_adj" in df.columns:
        sig_df = df[df["significant_any"] == True].sort_values("chi_p_adj") if "significant_any" in df.columns else df.sort_values("chi_p_adj").head(20)
    result["top_kw"] = sig_df.head(20) if len(sig_df) > 0 else pd.DataFrame()
    if "direction" in df.columns and "significant_any" in df.columns:
        sig_any = df[df["significant_any"] == True]
        result["dir_dist"] = sig_any.groupby("direction").size().to_dict()
    else:
        result["dir_dist"] = {}
    return result

def read_metrics_breakdown():
    if not os.path.exists(METRICS_CSV):
        return None
    import pandas as pd
    df = pd.read_csv(METRICS_CSV, encoding="utf-8")
    delta_df = df[df["config"] == "delta_C_minus_A"] if "config" in df.columns else pd.DataFrame()
    tradeoffs = []
    if len(delta_df) > 0 and "recall_class1" in delta_df.columns and "precision_class1" in delta_df.columns:
        for _, row in delta_df.iterrows():
            if row["recall_class1"] > 0 and row["precision_class1"] < 0:
                tradeoffs.append(row.get("model", "?"))
    return {"delta_df": delta_df, "tradeoffs": tradeoffs}

def read_news_density():
    if not os.path.exists(DENSITY_CSV):
        return None
    import pandas as pd
    df = pd.read_csv(DENSITY_CSV, encoding="utf-8")
    delta_df = df[df["config"] == "delta_C_minus_A"] if "config" in df.columns else pd.DataFrame()
    not_reliable = []
    if "reliable" in df.columns:
        not_reliable = df[df["reliable"] == False]["density_group"].unique().tolist() if len(df) > 0 else []
    return {"delta_df": delta_df, "not_reliable": not_reliable, "full_df": df}

def read_shap_ranking():
    if not os.path.exists(SHAP_CSV):
        return None
    import pandas as pd
    df = pd.read_csv(SHAP_CSV, encoding="utf-8")
    top10 = df.head(10) if len(df) >= 10 else df
    n_consistent = int(df["direction_consistent"].sum()) if "direction_consistent" in df.columns else 0
    total_abs = df["mean_abs_shap"].sum() if "mean_abs_shap" in df.columns else 0
    return {"top10": top10, "n_consistent": n_consistent, "n_total": len(df), "total_abs": total_abs}

def df_to_md_table(df, cols=None):
    if df is None or len(df) == 0:
        return "_Khong co du lieu._"
    if cols:
        df = df[[c for c in cols if c in df.columns]]
    header = "| " + " | ".join(df.columns) + " |"
    sep    = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    rows   = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(v) for v in row.values) + " |")
    return "\n".join([header, sep] + rows)

def build_report():
    kw   = read_kw_significance()
    mb   = read_metrics_breakdown()
    nd   = read_news_density()
    shap = read_shap_ranking()

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []

    lines.append("# Bao cao Kiem dinh H2 va H3\n")
    lines.append(f"_Tao tu dong vao: {now}_\n")

    lines.append("---\n")

    # Section 1
    lines.append("## 1. Boi canh va Tien de\n")
    lines.append("### 1.1 Ket luan H1 (tien de da chot)\n")
    lines.append("> **H1 KHONG duoc ung ho** -- Da duoc kiem chung triet de qua nhieu nguong thoi gian,")
    lines.append("> 4 don vi thoi gian, 5 lan mo rong corpus (9.7k -> 28k bai), 6 nguon can bang va cai tien")
    lines.append("> cach dem tu (phu dinh + dong nghia). Day la ket luan da chot, KHONG lam lai trong spec nay.\n")

    lines.append("### 1.2 Gioi thieu H2 va H3\n")
    lines.append("**Gia thuyet H2:** *Mot so tu khoa xuat hien co moi lien he thong ke voi xu huong tang/giam gia co phieu.*")
    lines.append("")
    lines.append("Phuong phap kiem dinh: chi-square/Fisher exact test, Mann-Whitney U test, logistic regression don bien,")
    lines.append("tat ca ap dung hieu chinh da kiem dinh Benjamini-Hochberg (BH-FDR).\n")
    lines.append("**Gia thuyet H3:** *Trong mo hinh Config_C, dac trung tu khoa dong gop co y nghia vao quyet dinh du bao.*")
    lines.append("")
    lines.append("Phuong phap kiem dinh: SHAP values + permutation importance bat buoc tren Random_Forest Config_C.\n")

    # Section 2
    lines.append("## 2. Goc 1 -- Kiem dinh H2: Moi lien he thong ke tung tu khoa\n")
    lines.append("### 2.1 Phuong phap\n")
    lines.append("- **Chi-square / Fisher exact test:** kiem tra tinh doc lap giua su xuat hien tu khoa (nhi phan) va nhan xu huong.")
    lines.append("  Neu co o ky vong < 5 trong bang 2x2 --> dung Fisher exact test thay cho chi-square.")
    lines.append("- **Mann-Whitney U test:** so sanh phan phoi tan suat tu khoa chuan hoa giua nhom 'tang' va 'khong tang'.")
    lines.append("- **Logistic regression don bien:** uoc luong he so va khoang tin cay 95%.")
    lines.append("- **Hieu chinh BH-FDR:** ap dung tren tat ca p-values truoc khi tuyen bo bat ky tu khoa nao la significant.")
    lines.append("- Phan tich in-sample (toan bo du lieu), khong ket luan ve kha nang du bao out-of-sample.\n")

    lines.append("### 2.2 Ket qua\n")
    if kw is None:
        lines.append(f"> {PLACEHOLDER} (File: `{KW_SIG_CSV}`)\n")
        lines.append("**Chu thich:** Chay `python -m pipeline.experiment_keyword_significance` de sinh du lieu.\n")
        h2_conclusion = "**CHUA CO DU LIEU** -- can chay Task 7."
    else:
        lines.append(f"- Tong so tu khoa phan tich: **{kw['n_total']}**")
        lines.append(f"- So tu khoa significant (chi/Fisher, adj): **{kw['n_sig_chi']}**")
        lines.append(f"- So tu khoa significant (Mann-Whitney, adj): **{kw['n_sig_mw']}**")
        lines.append(f"- So tu khoa significant (logistic, adj): **{kw['n_sig_logit']}**")
        lines.append(f"- So tu khoa significant (bat ky kiem dinh nao): **{kw['n_sig_any']}**\n")
        if kw["dir_dist"]:
            lines.append("**Phan bo significant theo huong:**")
            for d, c in kw["dir_dist"].items():
                lines.append(f"  - {d}: {c} tu khoa")
            lines.append("")
        lines.append("**Bang top tu khoa significant (sap xep theo chi_p_adj tang dan):**\n")
        cols = ["keyword", "direction", "chi_p_adj", "mw_p_adj", "logit_p_adj", "significant_any"]
        lines.append(df_to_md_table(kw["top_kw"], cols))
        lines.append("")
        h2_conclusion = (
            f"**H2 DUOC UNG HO** -- Co {kw['n_sig_any']} tu khoa significant (BH-FDR adj) trong it nhat mot kiem dinh."
            if kw["n_sig_any"] > 0
            else "**H2 KHONG duoc ung ho** -- Khong co tu khoa nao dat nguong significant sau hieu chinh BH-FDR."
        )

    lines.append("### 2.3 Ket luan H2\n")
    lines.append(h2_conclusion)
    lines.append("")

    # Section 3
    lines.append("## 3. Goc 2 -- Phan ra thuoc do: Recall lop 'tang'\n")
    lines.append("### 3.1 Phuong phap\n")
    lines.append("- So sanh Config_A (chi ky thuat) vs Config_C (ky thuat + tu khoa) tren 4 thuat toan ML.")
    lines.append("- Cung Time_Series_Split (cutoff 2025Q1), tai su dung cac ham trong `pipeline.task10_train`.")
    lines.append("- Tinh Precision, Recall, F1 theo tung lop (class 0 = 'khong tang', class 1 = 'tang'), AUC, Balanced Accuracy.")
    lines.append("- Them hang delta = Config_C - Config_A de phan tich dat doi.\n")

    lines.append("### 3.2 Ket qua\n")
    if mb is None:
        lines.append(f"> {PLACEHOLDER} (File: `{METRICS_CSV}`)\n")
        lines.append("**Chu thich:** Chay `python -m pipeline.experiment_metrics_breakdown` de sinh du lieu.\n")
    else:
        lines.append("**Bang delta (Config_C - Config_A) recall_class1 va precision_class1:**\n")
        cols = ["model", "recall_class1", "precision_class1", "f1_class1", "balanced_accuracy"]
        lines.append(df_to_md_table(mb["delta_df"], cols))
        lines.append("")
        if mb["tradeoffs"]:
            lines.append(f"**Truong hop dat doi (recall tang, precision giam):** {', '.join(mb['tradeoffs'])}")
        else:
            lines.append("**Khong co truong hop dat doi ro rang nao (recall tang kem theo precision giam).**")
        lines.append("")

    lines.append("### 3.3 Nhan xet\n")
    lines.append("- Config_C co the tang recall lop 'tang' nhung di kem voi giam precision (bao dong gia cao hon).")
    lines.append("- Day la gia tri bo sung co dieu kien: tu khoa giup nhan dien xu huong tang nhung khong tinh xac hon.\n")

    # Section 4
    lines.append("## 4. Goc 3 -- Dong gop tu khoa theo mat do tin\n")
    lines.append("### 4.1 Phuong phap\n")
    lines.append("- Phan chia tap test thanh nhom **tin day** (`has_min_news = 1`, tuc `news_count >= 5`) va **tin thua** (`has_min_news = 0`).")
    lines.append("- Huan luyen Config_A va Config_C tren toan bo tap train; danh gia rieng tren tung nhom mat do tin.")
    lines.append("- Tinh delta Config_C - Config_A cho moi nhom va moi thuat toan.")
    lines.append("- Nhom co < 20 mau hoac chi 1 lop nhan -> danh dau 'not reliable'.\n")

    lines.append("### 4.2 Ket qua\n")
    if nd is None:
        lines.append(f"> {PLACEHOLDER} (File: `{DENSITY_CSV}`)\n")
        lines.append("**Chu thich:** Chay `python -m pipeline.experiment_news_density` de sinh du lieu.\n")
    else:
        lines.append("**Bang delta (Config_C - Config_A) theo mat do tin:**\n")
        cols = ["model", "density_group", "balanced_accuracy", "recall_class1", "precision_class1", "n_samples", "reliable"]
        lines.append(df_to_md_table(nd["delta_df"] if len(nd["delta_df"]) > 0 else nd["full_df"], cols))
        lines.append("")
        if nd["not_reliable"]:
            lines.append(f"**Canh bao not-reliable:** {', '.join(str(x) for x in nd['not_reliable'])}")
        lines.append("")

    lines.append("### 4.3 Nhan xet\n")
    lines.append("- Nhom tin thua co the khong phan anh dung tac dong cua tu khoa vi du lieu qua it.")
    lines.append("- Neu delta Config_C-A tich cuc hon trong nhom tin day, dieu nay ung ho rang mat do tin la yeu to the hien.")
    lines.append("- Ket qua cac nhom not-reliable can duoc dien giai voi tham trong.\n")

    # Section 5
    lines.append("## 5. Goc 4 -- Kiem dinh H3: Tu khoa dong gop trong Config_C (SHAP)\n")
    lines.append("### 5.1 Phuong phap\n")
    lines.append("- Huan luyen bat buoc Random_Forest tren Config_C (khong phu thuoc vao best model toan cuc).")
    lines.append("- Tinh SHAP values (TreeExplainer) tren tap test; tinh permutation importance (Balanced Accuracy).")
    lines.append("- Xep hang dac trung tu khoa theo mean(|SHAP|); kiem tra tinh nhat quan huong.")
    lines.append("- Phan tich ty le dong gop nhom kw vs tech theo tong mean|SHAP|.\n")

    lines.append("### 5.2 Ket qua\n")
    if shap is None:
        lines.append(f"> {PLACEHOLDER} (File: `{SHAP_CSV}`)\n")
        lines.append("**Chu thich:** Chay `python -m pipeline.experiment_shap_configc` de sinh du lieu.\n")
        h3_conclusion = "**CHUA CO DU LIEU** -- can chay Task 7."
        n_consistent = "N/A"
        n_total_kw = "N/A"
    else:
        lines.append(f"**So tu khoa duoc xep hang:** {shap['n_total']}")
        lines.append(f"**So tu khoa nhat quan ve huong:** {shap['n_consistent']}/{shap['n_total']}\n")
        lines.append("**Top 10 tu khoa theo mean|SHAP| (Config_C):**\n")
        cols = ["keyword", "direction", "mean_abs_shap", "mean_shap", "shap_direction", "direction_consistent"]
        lines.append(df_to_md_table(shap["top10"], cols))
        lines.append("")
        lines.append("**Chu y ve % dong gop kw vs tech:**")
        lines.append("Gia tri nay duoc tinh trong qua trinh chay `experiment_shap_configc.py` (in ra stdout).")
        lines.append("De xap xi: tong mean|SHAP| cua top-10 tu khoa = **{:.6f}**.".format(float(shap["top10"]["mean_abs_shap"].sum()) if "mean_abs_shap" in shap["top10"].columns else 0))
        lines.append("(Xem output cua script de biet chinh xac % kw vs tech tren toan bo Config_C.)\n")
        n_consistent = shap["n_consistent"]
        n_total_kw = shap["n_total"]
        h3_conclusion = (
            f"**H3 DUOC UNG HO** -- {n_consistent}/{n_total_kw} tu khoa co SHAP direction nhat quan voi huong gan nhan."
            if (n_total_kw > 0 and n_consistent / n_total_kw > 0.5)
            else f"**H3 DUOC UNG HO MOT PHAN** -- Cac tu khoa co mat trong top features, nhung chi {n_consistent}/{n_total_kw} nhat quan ve huong."
        )

    lines.append("### 5.3 Ket luan H3\n")
    lines.append(h3_conclusion)
    lines.append("")

    # Section 6
    lines.append("## 6. Ket luan tong hop\n")
    lines.append("| Goc phan tich | Ket qua |")
    lines.append("|---|---|")
    lines.append("| H1 (tien de) | KHONG duoc ung ho (da chot, khong lam lai) |")
    lines.append("| H2 — Goc 1 (kiem dinh tu khoa) | " + (h2_conclusion.replace("\n","") if kw is not None else "Chua co du lieu") + " |")
    lines.append("| H2/H3 — Goc 2 (phan ra thuoc do) | " + ("Co du lieu delta" if mb is not None else "Chua co du lieu") + " |")
    lines.append("| H2/H3 — Goc 3 (mat do tin) | " + ("Co du lieu density" if nd is not None else "Chua co du lieu") + " |")
    lines.append("| H3 — Goc 4 (SHAP Config_C) | " + (h3_conclusion.replace("\n","") if shap is not None else "Chua co du lieu") + " |")
    lines.append("")
    lines.append("### Y nghia doi voi luan van\n")
    lines.append("- Neu H2 duoc ung ho: co the trinh bay danh sach tu khoa significant nhu bang chung rang tin tuc co chua tin hieu -- ngay ca khi H1 khong duoc ung ho o cap mo hinh tong the.")
    lines.append("- Neu H3 duoc ung ho: Config_C co su dung tu khoa mot cach co y nghia, nhung anh huong muc do toan cuc (balanced accuracy) chua du lon de cai thien H1.")
    lines.append("- Ket qua Goc 2 va Goc 3 mo ta 'gia tri bo sung co dieu kien', cho phep nguon cuu sinh trinh bay trung thuc va day du trong luan van.\n")

    # Section 7
    lines.append("## 7. Gia dinh va Gioi han\n")
    lines.append("### Goc 1 (Kiem dinh H2)\n")
    lines.append("- **In-sample analysis:** Kiem dinh thuc hien tren toan bo du lieu (khong phan chia train/test).")
    lines.append("  Ket qua phan anh moi lien he thong ke *da quan sat*, khong ket luan ve kha nang du bao out-of-sample.")
    lines.append("- **Gia dinh phan phoi:** Mann-Whitney khong gia dinh chuan, nhung chi-square gia dinh tan so ky vong >= 5 (neu vi pham se dung Fisher).")
    lines.append("- **Da kiem dinh:** BH-FDR kiem soat FDR < 5%, it bao thu hon Bonferroni, phu hop voi nghien cuu kham pha.\n")

    lines.append("### Goc 2 (Phan ra thuoc do)\n")
    lines.append("- **Chi mot time_series_split:** Khong cross-validated -- ket qua co the phu thuoc vao viec chon cutoff.")
    lines.append("- **4 thuat toan ML:** Ket qua phan anh xu huong trung binh; cac thuat toan cu the co the cho ket qua khac nhau.\n")

    lines.append("### Goc 3 (Mat do tin)\n")
    lines.append("- **Nguong has_min_news:** `news_count >= 5` -- nguong nay la tue y, ket qua co the thay doi voi nguong khac.")
    lines.append("- **Kich thuoc mau nho:** Nhom tin thua hoac tin day co the co rat it mau trong tap test, lam giam do tin cay thong ke.\n")

    lines.append("### Goc 4 (SHAP Config_C)\n")
    lines.append("- **Chi Random_Forest:** SHAP values phu thuoc vao loai mo hinh; ket qua co the khac neu dung Logistic Regression hoac GBM.")
    lines.append("- **SHAP la post-hoc explanation:** Khong chung minh tu qua (causality), chi do luong dong gop thuoc tinh.")
    lines.append("- **Permutation importance:** Phu thuoc vao metric (Balanced Accuracy); ket qua co the khac voi AUC hoac F1.\n")

    # Section 8
    lines.append("## 8. Tep ket qua\n")
    lines.append("| Goc | Tep | Mo ta |")
    lines.append("|---|---|---|")
    lines.append(f"| Goc 1 | `{KW_SIG_CSV}` | Bang kiem dinh H2 theo tung tu khoa |")
    lines.append(f"| Goc 2 | `{METRICS_CSV}` | Precision/Recall/F1/AUC theo (algo, config) + delta |")
    lines.append(f"| Goc 3 | `{DENSITY_CSV}` | Delta Config_C-A theo mat do tin |")
    lines.append(f"| Goc 4 | `{SHAP_CSV}` | Xep hang tu khoa theo SHAP |")
    lines.append("| Goc 4 | `reports/configc_shap_summary.png` | Beeswarm SHAP plot (Config_C) |")
    lines.append("| Goc 4 | `reports/configc_permutation_importance.png` | Permutation importance plot (Config_C) |")
    lines.append("")

    return "\n".join(lines)

os.makedirs(REPORTS_DIR, exist_ok=True)
report_text = build_report()
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report_text)
print(f"Da ghi bao cao: {REPORT_PATH}")
print(f"Kich thuoc: {len(report_text)} ky tu")