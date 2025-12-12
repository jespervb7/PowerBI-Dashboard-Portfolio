import pbir_utils as pbir

pbip_directory = r"C:\git\PowerBI-Dashboard-Portfolio\dashboards\Personal\Finances\Finances semantic model\Finaces semantic model.Report"
output_csv_path  = r"C:\git\PowerBI-Dashboard-Portfolio\data\finances_pbir_metadata.csv"

# pbir.export_pbir_metadata_to_csv(
#     directory_path=pbip_directory,
#     csv_output_path=output_csv_path,
#     filters={
#         "Report": {},
#         "Page Name": {},
#         "Page ID": {},
#         "Table": {},
#         "Column or Measure": {},
#         "Expression": {},
#         "Used In": {},
#         "Used In Detail": {},
#         "ID": {},
#     },
# )

pbir.sanitize_powerbi_report(
    pbip_directory,
    [
        "cleanup_invalid_bookmarks",
        "remove_unused_measures",
        "remove_unused_bookmarks",
        "remove_unused_custom_visuals",
        "disable_show_items_with_no_data",
        "hide_tooltip_pages",
        "set_first_page_as_active",
        "remove_empty_pages",
        "remove_hidden_visuals_never_shown",
        "standardize_pbir_folders",
    ],
    dry_run=True,
)