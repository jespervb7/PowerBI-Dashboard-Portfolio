# PowerBI-Dashboard-Portfolio
This repository contains a portfolio of the dashboards I have created. This to showcase my skills as an analytics engineer and some of my data consultant skills.

### Credit to Rui Romano for his BPA actions repository!

Thanks to Rui Romano I started implemting this relatively easy action in my workflow. Having automated checks on my repository is very important from a Q&A standpoint.

## Surrogate Key Standards

Surrogate keys are system-generated identifiers that uniquely represent each record in a dimension table. Unlike natural or business keys, they remain stable even when source systems or business rules change. This stability ensures reliable joins between fact and dimension tables, and provides a foundation for consistent analytics and reporting.

To maintain data integrity and ensure consistent handling of exceptional or missing data, each dimension table should include a standard set of **reserved surrogate key values**. These default values define clear semantics for non-standard conditions encountered during ETL processing.

### Reserved surrogate key values

| Surrogate Key | Meaning | Typical Use Case |
|---:|---|---|
| **-1** | **Unknown** | Used when the corresponding dimension record is missing or not found during ETL. Example: a sales fact references a customer not yet loaded in `dim_customer`. |
| **-2** | **Not Applicable** | Used when the dimension does not logically apply to the fact record. Example: a transaction with no associated promotion uses `promotion_sk = -2`. |
| **-3** | **Pending / To Be Determined** | Used when a dimension record is expected later. Common for late-arriving dimensions or delayed data feeds. |
| **-4** | **Error / Invalid** | Used when a lookup fails validation or mapping due to bad source data. This key helps identify and track data quality issues. |
| **-5** | **Default / Fallback** | A general fallback key, reserved for use when no other condition applies. Should be used sparingly. |

---

### Example — `dim_customer`

```text
| customer_sk | customer_id | customer_name    | customer_type |
|------------:|------------:|------------------|---------------|
|         -1  | NULL        | Unknown Customer | Unknown       |
|         -2  | NULL        | Not Applicable   | N/A           |
|          1  | 1001        | Alice Smith      | Retail        |
|          2  | 1002        | Bob Jones        | Wholesale     |
```