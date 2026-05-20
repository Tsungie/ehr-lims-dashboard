# 🔬 EHR-LIMS Viral Load Validation Dashboard

## 📖 Project Overview
This project is an interactive data dashboard designed to evaluate the progress and data integrity of the EHR (Electronic Health Record) and LIMS (Laboratory Information Management System) integration. 

Following the activation of multiple sites in 2025, this retrospective analysis aims to track Viral Load (VL) sample data as it moves through the healthcare pipeline. The primary goal is to identify and quantify data leakage (data loss) between manual collection, electronic capture, and final centralized submission.

---

## 🔄 The Data Pipeline
The workflow tracks a patient's Viral Load sample through three critical stages:

1. 📝 **Paper Collection:** The sample is physically taken at the facility and recorded on paper forms.
   * *Metric:* `Total VL Samples Collected (BAs)`
2. 💻 **EHR Entry:** The sample is sent to the lab, and the order is supposed to be digitally captured in the local EHR system.
   * *Metric:* `Total Orders Captured in E-HR (BAs)`
3. ☁️ **SHR Submission:** The EHR data is finally transmitted to the Shared Health Record (SHR).
   * *Metric:* `Total Samples submitted to SHR (Jima)`

---

## 📉 Identifying Data Gaps
By comparing the metrics at each stage of the pipeline, the dashboard highlights two critical areas of data loss:

* **Gap 1 (Paper vs. EHR):** Samples that were collected on paper but *failed to be entered* into the EHR system.
* **Gap 2 (EHR vs. SHR):** Orders that were captured in the EHR but *failed to successfully submit* to the SHR.

---

## 📐 Analysis Business Rules
* **1-Month Activation Offset:** To account for transition periods and ensure fair evaluation, analysis for any given facility begins **exactly one month after** its official activation date. 
  * *Example:* If a clinic's EHR was activated in November, its data analysis strictly begins in December.

---

## 📊 Dashboard Features
* **Interactive Visualizations:** Dynamic charts mapping the flow of data and pinpointing exact drop-off stages.
* **Leakage Leaderboards:** Automatically identifies and ranks the worst-performing facilities with the highest rates of data loss, allowing for targeted interventions.
* **Granular Filtering:** Users can drill down and filter metrics by specific clinics or districts to view localized performance trends.
