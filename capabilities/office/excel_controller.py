import logging
from typing import List, Dict, Any, Optional
import pythoncom
import win32com.client
from llm.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelController:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client
        self.excel = None
        self.workbook = None
        self.ws = None
        self._connected = False
        self._connect_to_excel()
        if self.llm_client:
            logger.info("ExcelController initialized with LLMClient")
        else:
            logger.warning("ExcelController initialized without LLMClient - AI actions will not work")
        logger.info("ExcelController initialized successfully")

    def _connect_to_excel(self) -> bool:
        try:
            pythoncom.CoInitialize()

            try:
                self.excel = win32com.client.GetActiveObject("Excel.Application")
                logger.info("Connected to existing Excel instance")
            except Exception:
                logger.info("No existing Excel instance found, creating new one")
                self.excel = win32com.client.Dispatch("Excel.Application")
                self.excel.Visible = True
                logger.info("Created new Excel instance")

            self._connected = True
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Excel: {e}")
            self._connected = False
            return False

    def _get_workbook(self) -> bool:
        try:
            if self.excel is None:
                logger.error("Excel instance not connected")
                return False
            if self.excel.Workbooks.Count == 0:
                logger.warning("No workbooks open, creating new one")
                self.workbook = self.excel.Workbooks.Add()
                self.ws = self.workbook.ActiveSheet
                return True
            self.workbook = self.excel.ActiveWorkbook
            self.ws = self.workbook.ActiveSheet
            return True
        except Exception as e:
            logger.error(f"Error getting workbook: {e}")
            return False

    def _ensure_workbook(self) -> bool:
        try:
            if self.excel is None:
                logger.error("Excel instance not connected")
                return False
            if self.excel.Workbooks.Count == 0:
                logger.info("No workbooks open, creating new one")
                self.workbook = self.excel.Workbooks.Add()
                self.ws = self.workbook.ActiveSheet
                return True
            self.workbook = self.excel.ActiveWorkbook
            self.ws = self.workbook.ActiveSheet
            return True
        except Exception as e:
            logger.error(f"Failed to ensure workbook exists: {e}")
            return False

    def _get_active_worksheet(self):
        if not self._ensure_workbook():
            return None
        return self.workbook.ActiveSheet

    def _get_selected_range_text(self) -> Optional[str]:
        try:
            if not self._ensure_workbook():
                return None
            selection = self.excel.Selection
            values = selection.Value
            if values is None:
                return ""
            if not isinstance(values, tuple):
                return str(values)
            rows = []
            for row in values:
                if isinstance(row, tuple):
                    rows.append("\t".join("" if cell is None else str(cell) for cell in row))
                else:
                    rows.append("" if row is None else str(row))
            return "\n".join(rows)
        except Exception as e:
            logger.error(f"Failed to read selected range: {e}")
            return None

    def supported_actions(self) -> List[str]:
        return [
            "create_workbook",
            "create_new",
            "open_workbook",
            "save_workbook",
            "save_workbook_as",
            "close_workbook",
            "add_worksheet",
            "delete_worksheet",
            "rename_worksheet",
            "select_worksheet",
            "write_cell",
            "write_range",
            "clear_cell",
            "clear_range",
            "select_cell",
            "select_range",
            "get_cell_value",
            "merge_cells",
            "unmerge_cells",
            "align_left",
            "align_center",
            "align_right",
            "bold_cells",
            "italic_cells",
            "underline_cells",
            "font_size",
            "currency_format",
            "number_format",
            "format_cells",
            "autofit_columns",
            "apply_sum",
            "apply_average",
            "apply_formula",
            "apply_if",
            "apply_vlookup",
            "sort_range",
            "apply_filter",
            "remove_filter",
            "create_table",
            "create_chart",
            "generate_sample_data",
            "explain_formula",
            "summarize_table",
            "clean_duplicates"
        ]

    def execute(self, action: str, target: str = "", parameters: Dict[str, Any] = None) -> bool:
        if parameters is None:
            parameters = {}

        logger.info(f"Executing Excel action: {action}, target: {target}, parameters: {parameters}")

        action_map = {
            "create_workbook": self._create_workbook,
            "create_new": self._create_workbook,
            "open_workbook": self._open_workbook,
            "save_workbook": self._save_workbook,
            "save_workbook_as": self._save_workbook_as,
            "close_workbook": self._close_workbook,
            "add_worksheet": self._add_worksheet,
            "delete_worksheet": self._delete_worksheet,
            "rename_worksheet": self._rename_worksheet,
            "select_worksheet": self._select_worksheet,
            "write_cell": self._write_cell,
            "write_range": self._write_range,
            "clear_cell": self._clear_cell,
            "clear_range": self._clear_range,
            "select_cell": self._select_cell,
            "select_range": self._select_range,
            "get_cell_value": self._get_cell_value,
            "merge_cells": self._merge_cells,
            "unmerge_cells": self._unmerge_cells,
            "align_left": self._align_left,
            "align_center": self._align_center,
            "align_right": self._align_right,
            "bold_cells": self._bold_cells,
            "italic_cells": self._italic_cells,
            "underline_cells": self._underline_cells,
            "font_size": self._font_size,
            "currency_format": self._currency_format,
            "number_format": self._number_format,
            "format_cells": self._format_cells,
            "autofit_columns": self._autofit_columns,
            "apply_sum": self._apply_sum,
            "apply_average": self._apply_average,
            "apply_formula": self._apply_formula,
            "apply_if": self._apply_if,
            "apply_vlookup": self._apply_vlookup,
            "sort_range": self._sort_range,
            "apply_filter": self._apply_filter,
            "remove_filter": self._remove_filter,
            "create_table": self._create_table,
            "create_chart": self._create_chart,
            "generate_sample_data": self._generate_sample_data,
            "explain_formula": self._explain_formula,
            "summarize_table": self._summarize_table,
            "clean_duplicates": self._clean_duplicates
        }

        if action not in action_map:
            logger.error(f"Unsupported action: {action}")
            return False

        try:
            return action_map[action](parameters)
        except Exception as e:
            logger.error(f"Error executing {action}: {e}")
            return False

    def _create_workbook(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            self.workbook = self.excel.Workbooks.Add()
            self.ws = self.workbook.ActiveSheet
            logger.info("Created new workbook")
            return True
        except Exception as e:
            logger.error(f"Failed to create workbook: {e}")
            return False

    def _open_workbook(self, parameters: Dict[str, Any]) -> bool:
        try:
            filepath = parameters.get("filepath", "")
            if not filepath:
                logger.error("No filepath provided for open_workbook")
                return False
            self.workbook = self.excel.Workbooks.Open(filepath)
            self.ws = self.workbook.ActiveSheet
            logger.info(f"Opened workbook: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to open workbook: {e}")
            return False

    def _save_workbook(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            self.workbook.Save()
            logger.info("Workbook saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save workbook: {e}")
            return False

    def _save_workbook_as(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            filepath = parameters.get("filepath", "")
            if not filepath:
                logger.error("No filepath provided for save_workbook_as")
                return False
            self.workbook.SaveAs(filepath)
            logger.info(f"Workbook saved as: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save workbook as: {e}")
            return False

    def _close_workbook(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._get_workbook():
                return False
            self.workbook.Close()
            self.workbook = None
            self.ws = None
            logger.info("Workbook closed")
            return True
        except Exception as e:
            logger.error(f"Failed to close workbook: {e}")
            return False

    def _add_worksheet(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            name = parameters.get("name", "")
            new_sheet = self.workbook.Worksheets.Add()
            if name:
                new_sheet.Name = name
            self.ws = new_sheet
            logger.info(f"Added worksheet: {new_sheet.Name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add worksheet: {e}")
            return False

    def _delete_worksheet(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            name = parameters.get("name", "")
            if not name:
                logger.error("No name provided for delete_worksheet")
                return False
            self.excel.DisplayAlerts = False
            self.workbook.Worksheets(name).Delete()
            self.excel.DisplayAlerts = True
            logger.info(f"Deleted worksheet: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete worksheet: {e}")
            return False

    def _rename_worksheet(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            name = parameters.get("name", "")
            new_name = parameters.get("new_name", "")
            if not new_name:
                logger.error("No new_name provided for rename_worksheet")
                return False
            sheet = self.workbook.Worksheets(name) if name else self.ws
            sheet.Name = new_name
            logger.info(f"Renamed worksheet to: {new_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to rename worksheet: {e}")
            return False

    def _select_worksheet(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            name = parameters.get("name", "")
            if not name:
                logger.error("No name provided for select_worksheet")
                return False
            self.ws = self.workbook.Worksheets(name)
            self.ws.Activate()
            logger.info(f"Selected worksheet: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to select worksheet: {e}")
            return False

    def _write_cell(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            cell = parameters.get("cell", "")
            value = parameters.get("value", "")
            if not cell:
                logger.error("No cell provided for write_cell")
                return False
            self.ws.Range(cell).Value = value
            logger.info(f"Wrote value to {cell}: {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to write cell: {e}")
            return False

    def _write_range(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            anchor_cell = parameters.get("cell", "A1")
            values = parameters.get("values", [])
            if not values:
                logger.error("No values provided for write_range")
                return False
            rows = len(values)
            cols = len(values[0]) if isinstance(values[0], list) else 1
            data = [row if isinstance(row, list) else [row] for row in values]
            start_cell = self.ws.Range(anchor_cell)
            target_range = start_cell.Resize(rows, cols)
            target_range.Value = data
            logger.info(f"Wrote {rows}x{cols} range starting at {anchor_cell}")
            return True
        except Exception as e:
            logger.error(f"Failed to write range: {e}")
            return False

    def _clear_cell(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            cell = parameters.get("cell", "")
            if not cell:
                logger.error("No cell provided for clear_cell")
                return False
            self.ws.Range(cell).ClearContents()
            logger.info(f"Cleared cell: {cell}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cell: {e}")
            return False

    def _clear_range(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            range_ref = parameters.get("range", "")
            if not range_ref:
                logger.error("No range provided for clear_range")
                return False
            self.ws.Range(range_ref).ClearContents()
            logger.info(f"Cleared range: {range_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear range: {e}")
            return False

    def _select_cell(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            cell = parameters.get("cell", "")
            if not cell:
                logger.error("No cell provided for select_cell")
                return False
            self.ws.Range(cell).Select()
            logger.info(f"Selected cell: {cell}")
            return True
        except Exception as e:
            logger.error(f"Failed to select cell: {e}")
            return False

    def _select_range(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            range_ref = parameters.get("range", "")
            if not range_ref:
                logger.error("No range provided for select_range")
                return False
            self.ws.Range(range_ref).Select()
            logger.info(f"Selected range: {range_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to select range: {e}")
            return False

    def _get_cell_value(self, parameters: Dict[str, Any]) -> Optional[Any]:
        try:
            if not self._ensure_workbook():
                return None
            cell = parameters.get("cell", "")
            if not cell:
                logger.error("No cell provided for get_cell_value")
                return None
            value = self.ws.Range(cell).Value
            logger.info(f"Got value from {cell}: {value}")
            return value
        except Exception as e:
            logger.error(f"Failed to get cell value: {e}")
            return None

    def _merge_cells(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            range_ref = parameters.get("range", "")
            if not range_ref:
                logger.error("No range provided for merge_cells")
                return False
            self.ws.Range(range_ref).Merge()
            logger.info(f"Merged cells: {range_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to merge cells: {e}")
            return False

    def _unmerge_cells(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            range_ref = parameters.get("range", "")
            if not range_ref:
                logger.error("No range provided for unmerge_cells")
                return False
            self.ws.Range(range_ref).UnMerge()
            logger.info(f"Unmerged cells: {range_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to unmerge cells: {e}")
            return False

    def _target_range(self, parameters: Dict[str, Any]):
        range_ref = parameters.get("range", "") if parameters else ""
        if range_ref:
            return self.ws.Range(range_ref)
        return self.excel.Selection

    def _align_left(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            # xlLeft = -4131
            self._target_range(parameters).HorizontalAlignment = -4131
            logger.info("Aligned cells left")
            return True
        except Exception as e:
            logger.error(f"Failed to align left: {e}")
            return False

    def _align_center(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            # xlCenter = -4108
            self._target_range(parameters).HorizontalAlignment = -4108
            logger.info("Aligned cells center")
            return True
        except Exception as e:
            logger.error(f"Failed to align center: {e}")
            return False

    def _align_right(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            # xlRight = -4152
            self._target_range(parameters).HorizontalAlignment = -4152
            logger.info("Aligned cells right")
            return True
        except Exception as e:
            logger.error(f"Failed to align right: {e}")
            return False

    def _bold_cells(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            self._target_range(parameters).Font.Bold = True
            logger.info("Bolded cells")
            return True
        except Exception as e:
            logger.error(f"Failed to bold cells: {e}")
            return False

    def _italic_cells(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            self._target_range(parameters).Font.Italic = True
            logger.info("Italicized cells")
            return True
        except Exception as e:
            logger.error(f"Failed to italicize cells: {e}")
            return False

    def _underline_cells(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            # xlUnderlineStyleSingle = 2
            self._target_range(parameters).Font.Underline = 2
            logger.info("Underlined cells")
            return True
        except Exception as e:
            logger.error(f"Failed to underline cells: {e}")
            return False

    def _font_size(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            size = parameters.get("size")
            if not size:
                logger.error("No size provided for font_size")
                return False
            self._target_range(parameters).Font.Size = size
            logger.info(f"Applied font size: {size}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply font size: {e}")
            return False

    def _currency_format(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            fmt = parameters.get("format", "$#,##0.00") if parameters else "$#,##0.00"
            self._target_range(parameters).NumberFormat = fmt
            logger.info("Applied currency formatting")
            return True
        except Exception as e:
            logger.error(f"Failed to apply currency format: {e}")
            return False

    def _number_format(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            fmt = parameters.get("format", "")
            if not fmt:
                logger.error("No format provided for number_format")
                return False
            self._target_range(parameters).NumberFormat = fmt
            logger.info(f"Applied number format: {fmt}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply number format: {e}")
            return False

    def _format_cells(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False

            target = self._target_range(parameters)

            if parameters.get("bold", False):
                target.Font.Bold = True
                logger.info("Applied bold")

            if parameters.get("italic", False):
                target.Font.Italic = True
                logger.info("Applied italic")

            if parameters.get("underline", False):
                # xlUnderlineStyleSingle = 2
                target.Font.Underline = 2
                logger.info("Applied underline")

            alignment = parameters.get("alignment")
            if alignment == "left":
                target.HorizontalAlignment = -4131
                logger.info("Applied left alignment")
            elif alignment == "center":
                target.HorizontalAlignment = -4108
                logger.info("Applied center alignment")
            elif alignment == "right":
                target.HorizontalAlignment = -4152
                logger.info("Applied right alignment")

            font_size = parameters.get("font_size")
            if font_size:
                target.Font.Size = font_size
                logger.info(f"Applied font size: {font_size}")

            number_format = parameters.get("number_format")
            if number_format:
                target.NumberFormat = number_format
                logger.info(f"Applied number format: {number_format}")

            logger.info("Formatting applied successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to format cells: {e}")
            return False

    def _autofit_columns(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            range_ref = parameters.get("range", "") if parameters else ""
            target = self.ws.Range(range_ref).EntireColumn if range_ref else self.ws.UsedRange.EntireColumn
            target.AutoFit()
            logger.info("Autofit columns")
            return True
        except Exception as e:
            logger.error(f"Failed to autofit columns: {e}")
            return False

    def _apply_sum(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            cell = parameters.get("cell", "")
            range_ref = parameters.get("range", "")
            if not cell or not range_ref:
                logger.error("cell and range are required for apply_sum")
                return False
            self.ws.Range(cell).Formula = f"=SUM({range_ref})"
            logger.info(f"Applied SUM formula at {cell} over {range_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply SUM formula: {e}")
            return False

    def _apply_average(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            cell = parameters.get("cell", "")
            range_ref = parameters.get("range", "")
            if not cell or not range_ref:
                logger.error("cell and range are required for apply_average")
                return False
            self.ws.Range(cell).Formula = f"=AVERAGE({range_ref})"
            logger.info(f"Applied AVERAGE formula at {cell} over {range_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply AVERAGE formula: {e}")
            return False

    def _apply_formula(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            cell = parameters.get("cell", "")
            formula = parameters.get("formula", "")
            if not cell or not formula:
                logger.error("cell and formula are required for apply_formula")
                return False
            if not formula.startswith("="):
                formula = f"={formula}"
            self.ws.Range(cell).Formula = formula
            logger.info(f"Applied formula at {cell}: {formula}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply formula: {e}")
            return False

    def _apply_if(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            cell = parameters.get("cell", "")
            condition = parameters.get("condition", "")
            true_value = parameters.get("true_value", "")
            false_value = parameters.get("false_value", "")
            if not cell or not condition:
                logger.error("cell and condition are required for apply_if")
                return False
            formula = f'=IF({condition},"{true_value}","{false_value}")'
            self.ws.Range(cell).Formula = formula
            logger.info(f"Applied IF formula at {cell}: {formula}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply IF formula: {e}")
            return False

    def _apply_vlookup(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            cell = parameters.get("cell", "")
            lookup_value = parameters.get("lookup_value", "")
            table_range = parameters.get("table_range", "")
            col_index = parameters.get("col_index", "")
            range_lookup = parameters.get("range_lookup", False)
            if not cell or not lookup_value or not table_range or not col_index:
                logger.error("cell, lookup_value, table_range and col_index are required for apply_vlookup")
                return False
            lookup_flag = "TRUE" if range_lookup else "FALSE"
            formula = f"=VLOOKUP({lookup_value},{table_range},{col_index},{lookup_flag})"
            self.ws.Range(cell).Formula = formula
            logger.info(f"Applied VLOOKUP formula at {cell}: {formula}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply VLOOKUP formula: {e}")
            return False

    def _sort_range(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            range_ref = parameters.get("range", "")
            column = parameters.get("column", 1)
            order = parameters.get("order", "asc")
            has_headers = parameters.get("has_headers", True)
            if not range_ref:
                logger.error("No range provided for sort_range")
                return False
            target_range = self.ws.Range(range_ref)
            key_range = target_range.Columns(column)
            # xlAscending = 1, xlDescending = 2
            sort_order = 2 if order == "desc" else 1
            # xlYes = 1, xlNo = 2
            header_flag = 1 if has_headers else 2
            target_range.Sort(Key1=key_range, Order1=sort_order, Header=header_flag)
            logger.info(f"Sorted range {range_ref} by column {column} ({order})")
            return True
        except Exception as e:
            logger.error(f"Failed to sort range: {e}")
            return False

    def _apply_filter(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            range_ref = parameters.get("range", "")
            target_range = self.ws.Range(range_ref) if range_ref else self.ws.UsedRange
            target_range.AutoFilter()
            logger.info(f"Applied filter to: {range_ref or 'used range'}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply filter: {e}")
            return False

    def _remove_filter(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            if self.ws.AutoFilterMode:
                self.ws.AutoFilterMode = False
            logger.info("Removed filter")
            return True
        except Exception as e:
            logger.error(f"Failed to remove filter: {e}")
            return False

    def _create_table(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            range_ref = parameters.get("range", "")
            name = parameters.get("name", "")
            has_headers = parameters.get("has_headers", True)
            if not range_ref:
                logger.error("No range provided for create_table")
                return False
            # xlSrcRange = 1, xlYes = 1, xlNo = 2
            header_flag = 1 if has_headers else 2
            table = self.ws.ListObjects.Add(1, self.ws.Range(range_ref), None, header_flag)
            if name:
                table.Name = name
            logger.info(f"Created table over {range_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            return False

    def _create_chart(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            range_ref = parameters.get("range", "")
            chart_type = parameters.get("chart_type", "column")
            title = parameters.get("title", "")
            if not range_ref:
                logger.error("No range provided for create_chart")
                return False

            chart_type_map = {
                "column": 51,
                "bar": 57,
                "line": 4,
                "pie": 5,
                "scatter": -4169,
                "area": 1,
                "doughnut": -4120
            }
            chart_type_value = chart_type_map.get(chart_type, 51)

            chart_obj = self.workbook.Charts.Add()
            chart_obj.SetSourceData(Source=self.ws.Range(range_ref))
            chart_obj.ChartType = chart_type_value
            # xlLocationAsObject = 2
            chart_obj.Location(Where=2, Name=self.ws.Name)

            if title:
                chart_obj.HasTitle = True
                chart_obj.ChartTitle.Text = title

            logger.info(f"Created {chart_type} chart from {range_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to create chart: {e}")
            return False

    def _generate_sample_data(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for generate_sample_data action")
                return False

            description = parameters.get("description", "")
            anchor_cell = parameters.get("cell", "A1")
            if not description:
                logger.warning("No description provided for generate_sample_data")
                return False

            logger.info("Starting AI sample data generation")
            result = self.llm_client.transform_text(description, "generate_sample_data", parameters)

            if result is None:
                logger.error("AI sample data generation failed")
                return False

            if not self._ensure_workbook():
                return False

            rows = [line for line in result.strip().splitlines() if line.strip()]
            data = [[cell.strip() for cell in row.split(",")] for row in rows]
            if not data:
                logger.warning("Generated sample data was empty")
                return False

            max_cols = max(len(row) for row in data)
            for row in data:
                while len(row) < max_cols:
                    row.append("")

            start_cell = self.ws.Range(anchor_cell)
            target_range = start_cell.Resize(len(data), max_cols)
            target_range.Value = data
            logger.info(f"Generated and wrote {len(data)}x{max_cols} sample data at {anchor_cell}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate sample data: {e}")
            return False

    def _explain_formula(self, parameters: Dict[str, Any] = None) -> Optional[str]:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for explain_formula action")
                return None

            if not self._ensure_workbook():
                return None

            cell = parameters.get("cell", "") if parameters else ""
            formula = self.ws.Range(cell).Formula if cell else self.excel.Selection.Formula

            if not formula or not str(formula).strip():
                logger.warning("No formula found to explain")
                return None

            logger.info("Starting AI formula explanation")
            result = self.llm_client.transform_text(str(formula), "explain_formula", parameters or {})

            if result is None:
                logger.error("AI formula explanation failed")
                return None

            logger.info("Formula explanation generated successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to explain formula: {e}")
            return None

    def _summarize_table(self, parameters: Dict[str, Any] = None) -> Optional[str]:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for summarize_table action")
                return None

            if not self._ensure_workbook():
                return None

            range_ref = parameters.get("range", "") if parameters else ""
            table_text = str(self.ws.Range(range_ref).Value) if range_ref else self._get_selected_range_text()

            if not table_text or not table_text.strip():
                logger.warning("No table data selected for summarize_table")
                return None

            logger.info("Starting AI table summarization")
            result = self.llm_client.transform_text(table_text, "summarize_table", parameters or {})

            if result is None:
                logger.error("AI table summarization failed")
                return None

            logger.info("Table summary generated successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to summarize table: {e}")
            return None

    def _clean_duplicates(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_workbook():
                return False
            range_ref = parameters.get("range", "")
            has_headers = parameters.get("has_headers", True)
            if not range_ref:
                logger.error("No range provided for clean_duplicates")
                return False
            target_range = self.ws.Range(range_ref)
            columns = tuple(range(1, target_range.Columns.Count + 1))
            # xlYes = 1, xlNo = 2
            header_flag = 1 if has_headers else 2
            target_range.RemoveDuplicates(Columns=columns, Header=header_flag)
            logger.info(f"Removed duplicate rows from {range_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to clean duplicates: {e}")
            return False


if __name__ == "__main__":
    print("Testing ExcelController")
    print("=" * 60)

    from llm.llm_client import LLMClient

    llm_client = LLMClient()
    controller = ExcelController(llm_client=llm_client)

    print(f"Supported actions: {controller.supported_actions()}")
    print("-" * 40)

    print("Test: Create workbook")
    result = controller.execute("create_workbook")
    print(f"Result: {result}")

    print("Test: Write cell")
    result = controller.execute("write_cell", parameters={"cell": "A1", "value": "Revenue"})
    print(f"Result: {result}")

    print("Test: Write range")
    result = controller.execute("write_range", parameters={"cell": "A2", "values": [[100], [200], [300]]})
    print(f"Result: {result}")

    print("Test: Apply SUM formula")
    result = controller.execute("apply_sum", parameters={"cell": "A5", "range": "A2:A4"})
    print(f"Result: {result}")

    print("Test: Currency format")
    result = controller.execute("currency_format", parameters={"range": "A2:A5"})
    print(f"Result: {result}")

    print("Test: Bold cells")
    result = controller.execute("bold_cells", parameters={"range": "A1"})
    print(f"Result: {result}")

    print("Test: Save workbook")
    result = controller.execute("save_workbook")
    print(f"Result: {result}")

    print("Test: Close workbook")
    result = controller.execute("close_workbook")
    print(f"Result: {result}")

    print("\nTest completed")
