import logging
import os
from typing import List, Dict, Any, Optional
import pythoncom
import win32com.client
from win32com.client import constants
from llm.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordController:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client
        self.word = None
        self.doc = None
        self._connected = False
        self._connect_to_word()
        if self.llm_client:
            logger.info("WordController initialized with LLMClient")
        else:
            logger.warning("WordController initialized without LLMClient - AI actions will not work")
        logger.info("WordController initialized successfully")

    def _connect_to_word(self) -> bool:
        try:
            pythoncom.CoInitialize()
            
            try:
                self.word = win32com.client.GetActiveObject("Word.Application")
                logger.info("Connected to existing Word instance")
            except:
                logger.info("No existing Word instance found, creating new one")
                self.word = win32com.client.Dispatch("Word.Application")
                self.word.Visible = True
                logger.info("Created new Word instance")
            
            self._connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Word: {e}")
            self._connected = False
            return False

    def _get_document(self) -> bool:
        try:
            if self.word is None:
                logger.error("Word instance not connected")
                return False
            if self.word.Documents.Count == 0:
                logger.warning("No documents open, creating new one")
                self.doc = self.word.Documents.Add()
                return True
            self.doc = self.word.ActiveDocument
            return True
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return False

    def _ensure_document(self) -> bool:
        try:
            if self.word is None:
                logger.error("Word instance not connected")
                return False
            if self.word.Documents.Count == 0:
                logger.info("No documents open, creating new one")
                self.doc = self.word.Documents.Add()
                return True
            self.doc = self.word.ActiveDocument
            return True
        except Exception as e:
            logger.error(f"Failed to ensure document exists: {e}")
            return False

    def _preserve_selection(self, func, *args, **kwargs):
        """Helper to preserve text selection after operations"""
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            start = selection.Start
            end = selection.End
            has_selection = (start != end)
            result = func(*args, **kwargs)
            if has_selection:
                selection.SetRange(start, end)
            return result
        except Exception as e:
            logger.error(f"Error in _preserve_selection: {e}")
            return False

    def _get_selected_text(self) -> Optional[str]:
        try:
            if not self._ensure_document():
                return None
            selection = self.word.Selection
            if selection.Type == constants.wdSelectionIP:
                logger.info("No text selected")
                return ""
            text = selection.Text
            logger.info(f"Got selected text: {text[:50]}...")
            return text
        except Exception as e:
            logger.error(f"Failed to get selected text: {e}")
            return None

    def _replace_selection(self, new_text: str) -> bool:
        try:
            if not self._ensure_document():
                return False
            if not new_text:
                logger.error("No text provided to replace selection")
                return False
            selection = self.word.Selection
            selection.Text = new_text
            logger.info(f"Replaced selected text with: {new_text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to replace selected text: {e}")
            return False

    def supported_actions(self) -> List[str]:
        return [
            "create_document",
            "create_new",
            "open_document",
            "save_document",
            "save_document_as",
            "close_document",
            "insert_blank_page",
            "insert_page_break",
            "select_all",
            "get_selected_text",
            "replace_selected_text",
            "insert_text",
            "delete_selected_text",
            "bold_selection",
            "italic_selection",
            "underline_selection",
            "align_left",
            "align_center",
            "align_right",
            "justify",
            "format_text",
            "undo",
            "redo",
            "rewrite",
            "summarize",
            "translate",
            "fix_grammar",
            "expand",
            "shorten",
            "convert_to_bullets",
            "convert_to_paragraph"
        ]

    def execute(self, action: str, target: str = "", parameters: Dict[str, Any] = None) -> bool:
        if parameters is None:
            parameters = {}
        
        logger.info(f"Executing Word action: {action}, target: {target}, parameters: {parameters}")
        
        action_map = {
            "create_document": self._create_document,
            "create_new": self._create_document,
            "open_document": self._open_document,
            "save_document": self._save_document,
            "save_document_as": self._save_document_as,
            "close_document": self._close_document,
            "insert_blank_page": self._insert_blank_page,
            "insert_page_break": self._insert_page_break,
            "select_all": self._select_all,
            "get_selected_text": self._get_selected_text,
            "replace_selected_text": self._replace_selected_text,
            "insert_text": self._insert_text,
            "delete_selected_text": self._delete_selected_text,
            "bold_selection": self._bold_selection,
            "italic_selection": self._italic_selection,
            "underline_selection": self._underline_selection,
            "align_left": self._align_left,
            "align_center": self._align_center,
            "align_right": self._align_right,
            "justify": self._justify,
            "format_text": self._format_text,
            "undo": self._undo,
            "redo": self._redo,
            "rewrite": self._rewrite_selection,
            "summarize": self._summarize_selection,
            "translate": self._translate_selection,
            "fix_grammar": self._fix_grammar,
            "expand": self._expand_selection,
            "shorten": self._shorten_selection,
            "convert_to_bullets": self._convert_to_bullets,
            "convert_to_paragraph": self._convert_to_paragraph
        }
        
        if action not in action_map:
            logger.error(f"Unsupported action: {action}")
            return False
        
        try:
            return action_map[action](parameters)
        except Exception as e:
            logger.error(f"Error executing {action}: {e}")
            return False

    def _create_document(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            self.doc = self.word.Documents.Add()
            logger.info("Created new document")
            return True
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            return False

    def _open_document(self, parameters: Dict[str, Any]) -> bool:
        try:
            filepath = parameters.get("filepath", "")
            if not filepath:
                logger.error("No filepath provided for open_document")
                return False
            self.doc = self.word.Documents.Open(filepath)
            logger.info(f"Opened document: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to open document: {e}")
            return False

    def _save_document(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            self.doc.Save()
            logger.info("Document saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            return False

    def _save_document_as(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_document():
                return False
            filepath = parameters.get("filepath", "")
            if not filepath:
                logger.error("No filepath provided for save_document_as")
                return False
            self.doc.SaveAs(filepath)
            logger.info(f"Document saved as: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save document as: {e}")
            return False

    def _close_document(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._get_document():
                return False
            self.doc.Close()
            self.doc = None
            logger.info("Document closed")
            return True
        except Exception as e:
            logger.error(f"Failed to close document: {e}")
            return False

    def _insert_blank_page(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            selection.InsertBreak(constants.wdPageBreak)
            logger.info("Inserted blank page")
            return True
        except Exception as e:
            logger.error(f"Failed to insert blank page: {e}")
            return False

    def _insert_page_break(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            selection.InsertBreak(constants.wdPageBreak)
            logger.info("Inserted page break")
            return True
        except Exception as e:
            logger.error(f"Failed to insert page break: {e}")
            return False

    def _select_all(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            self.word.Selection.WholeStory()
            logger.info("Selected all text")
            return True
        except Exception as e:
            logger.error(f"Failed to select all: {e}")
            return False

    def _get_selected_text(self, parameters: Dict[str, Any] = None) -> Optional[str]:
        try:
            if not self._ensure_document():
                return None
            selection = self.word.Selection
            if selection.Type == constants.wdSelectionIP:
                logger.info("No text selected")
                return ""
            text = selection.Text
            logger.info(f"Got selected text: {text[:50]}...")
            return text
        except Exception as e:
            logger.error(f"Failed to get selected text: {e}")
            return None

    def _replace_selected_text(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_document():
                return False
            new_text = parameters.get("text", "")
            if not new_text:
                logger.error("No text provided for replace_selected_text")
                return False
            selection = self.word.Selection
            selection.Text = new_text
            logger.info(f"Replaced selected text with: {new_text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to replace selected text: {e}")
            return False

    def _insert_text(self, parameters: Dict[str, Any]) -> bool:
        try:
            if not self._ensure_document():
                return False
            text = parameters.get("text", "")
            if not text:
                logger.error("No text provided for insert_text")
                return False
            self.word.Selection.Text = text
            logger.info(f"Inserted text: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to insert text: {e}")
            return False

    def _delete_selected_text(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            if selection.Type != constants.wdSelectionIP:
                selection.Delete()
                logger.info("Deleted selected text")
            else:
                logger.info("No text selected to delete")
            return True
        except Exception as e:
            logger.error(f"Failed to delete selected text: {e}")
            return False

    def _bold_selection(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            start = selection.Start
            end = selection.End
            has_selection = (start != end)
            selection.Font.Bold = True
            if has_selection:
                selection.SetRange(start, end)
            logger.info("Bolded selection")
            return True
        except Exception as e:
            logger.error(f"Failed to bold selection: {e}")
            return False

    def _italic_selection(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            start = selection.Start
            end = selection.End
            has_selection = (start != end)
            selection.Font.Italic = True
            if has_selection:
                selection.SetRange(start, end)
            logger.info("Italicized selection")
            return True
        except Exception as e:
            logger.error(f"Failed to italicize selection: {e}")
            return False

    def _underline_selection(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            start = selection.Start
            end = selection.End
            has_selection = (start != end)
            selection.Font.Underline = constants.wdUnderlineSingle
            if has_selection:
                selection.SetRange(start, end)
            logger.info("Underlined selection")
            return True
        except Exception as e:
            logger.error(f"Failed to underline selection: {e}")
            return False

    def _align_left(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            start = selection.Start
            end = selection.End
            has_selection = (start != end)
            self.word.Selection.ParagraphFormat.Alignment = constants.wdAlignParagraphLeft
            if has_selection:
                selection.SetRange(start, end)
            logger.info("Aligned left")
            return True
        except Exception as e:
            logger.error(f"Failed to align left: {e}")
            return False

    def _align_center(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            start = selection.Start
            end = selection.End
            has_selection = (start != end)
            self.word.Selection.ParagraphFormat.Alignment = constants.wdAlignParagraphCenter
            if has_selection:
                selection.SetRange(start, end)
            logger.info("Aligned center")
            return True
        except Exception as e:
            logger.error(f"Failed to align center: {e}")
            return False

    def _align_right(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            start = selection.Start
            end = selection.End
            has_selection = (start != end)
            self.word.Selection.ParagraphFormat.Alignment = constants.wdAlignParagraphRight
            if has_selection:
                selection.SetRange(start, end)
            logger.info("Aligned right")
            return True
        except Exception as e:
            logger.error(f"Failed to align right: {e}")
            return False

    def _justify(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            selection = self.word.Selection
            start = selection.Start
            end = selection.End
            has_selection = (start != end)
            self.word.Selection.ParagraphFormat.Alignment = constants.wdAlignParagraphJustify
            if has_selection:
                selection.SetRange(start, end)
            logger.info("Justified text")
            return True
        except Exception as e:
            logger.error(f"Failed to justify: {e}")
            return False

    def _format_text(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self._ensure_document():
                return False
            
            selection = self.word.Selection
            start = selection.Start
            end = selection.End
            has_selection = (start != end)
            
            success = True
            
            if parameters.get("bold", False):
                selection.Font.Bold = True
                logger.info("Applied bold")
            
            if parameters.get("italic", False):
                selection.Font.Italic = True
                logger.info("Applied italic")
            
            if parameters.get("underline", False):
                selection.Font.Underline = constants.wdUnderlineSingle
                logger.info("Applied underline")
            
            alignment = parameters.get("alignment")
            if alignment == "center":
                selection.ParagraphFormat.Alignment = constants.wdAlignParagraphCenter
                logger.info("Applied center alignment")
            elif alignment == "left":
                selection.ParagraphFormat.Alignment = constants.wdAlignParagraphLeft
                logger.info("Applied left alignment")
            elif alignment == "right":
                selection.ParagraphFormat.Alignment = constants.wdAlignParagraphRight
                logger.info("Applied right alignment")
            elif alignment == "justify":
                selection.ParagraphFormat.Alignment = constants.wdAlignParagraphJustify
                logger.info("Applied justify")
            
            font_size = parameters.get("font_size")
            if font_size:
                selection.Font.Size = font_size
                logger.info(f"Applied font size: {font_size}")
            
            if has_selection:
                selection.SetRange(start, end)
            
            logger.info("Formatting applied successfully")
            return success
            
        except Exception as e:
            logger.error(f"Failed to format text: {e}")
            return False

    def _undo(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            self.word.Undo()
            logger.info("Undo performed")
            return True
        except Exception as e:
            logger.error(f"Failed to undo: {e}")
            return False

    def _redo(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            self.word.Redo()
            logger.info("Redo performed")
            return True
        except Exception as e:
            logger.error(f"Failed to redo: {e}")
            return False

    def _rewrite_selection(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for rewrite action")
                return False
            
            logger.info("Getting selected text for rewrite")
            selected_text = self._get_selected_text()
            if not selected_text or not selected_text.strip():
                logger.warning("No text selected for rewrite")
                return False
            
            logger.info("Starting AI rewrite transformation")
            result = self.llm_client.transform_text(selected_text, "rewrite", parameters)
            
            if result is None:
                logger.error("AI rewrite transformation failed")
                return False
            
            logger.info("Replacing selected text with rewritten version")
            return self._replace_selection(result)
            
        except Exception as e:
            logger.error(f"Failed to rewrite selection: {e}")
            return False

    def _summarize_selection(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for summarize action")
                return False
            
            logger.info("Getting selected text for summarize")
            selected_text = self._get_selected_text()
            if not selected_text or not selected_text.strip():
                logger.warning("No text selected for summarize")
                return False
            
            logger.info("Starting AI summarize transformation")
            result = self.llm_client.transform_text(selected_text, "summarize", parameters)
            
            if result is None:
                logger.error("AI summarize transformation failed")
                return False
            
            logger.info("Replacing selected text with summarized version")
            return self._replace_selection(result)
            
        except Exception as e:
            logger.error(f"Failed to summarize selection: {e}")
            return False

    def _translate_selection(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for translate action")
                return False
            
            if parameters is None:
                parameters = {}
            
            if "language" not in parameters:
                parameters["language"] = "English"
            
            logger.info(f"Getting selected text for translate to {parameters['language']}")
            selected_text = self._get_selected_text()
            if not selected_text or not selected_text.strip():
                logger.warning("No text selected for translate")
                return False
            
            logger.info("Starting AI translate transformation")
            result = self.llm_client.transform_text(selected_text, "translate", parameters)
            
            if result is None:
                logger.error("AI translate transformation failed")
                return False
            
            logger.info("Replacing selected text with translated version")
            return self._replace_selection(result)
            
        except Exception as e:
            logger.error(f"Failed to translate selection: {e}")
            return False

    def _fix_grammar(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for fix_grammar action")
                return False
            
            logger.info("Getting selected text for grammar fix")
            selected_text = self._get_selected_text()
            if not selected_text or not selected_text.strip():
                logger.warning("No text selected for grammar fix")
                return False
            
            logger.info("Starting AI grammar fix transformation")
            result = self.llm_client.transform_text(selected_text, "fix_grammar", parameters)
            
            if result is None:
                logger.error("AI grammar fix transformation failed")
                return False
            
            logger.info("Replacing selected text with grammar-fixed version")
            return self._replace_selection(result)
            
        except Exception as e:
            logger.error(f"Failed to fix grammar in selection: {e}")
            return False

    def _expand_selection(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for expand action")
                return False
            
            logger.info("Getting selected text for expansion")
            selected_text = self._get_selected_text()
            if not selected_text or not selected_text.strip():
                logger.warning("No text selected for expansion")
                return False
            
            logger.info("Starting AI expand transformation")
            result = self.llm_client.transform_text(selected_text, "expand", parameters)
            
            if result is None:
                logger.error("AI expand transformation failed")
                return False
            
            logger.info("Replacing selected text with expanded version")
            return self._replace_selection(result)
            
        except Exception as e:
            logger.error(f"Failed to expand selection: {e}")
            return False

    def _shorten_selection(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for shorten action")
                return False
            
            logger.info("Getting selected text for shortening")
            selected_text = self._get_selected_text()
            if not selected_text or not selected_text.strip():
                logger.warning("No text selected for shortening")
                return False
            
            logger.info("Starting AI shorten transformation")
            result = self.llm_client.transform_text(selected_text, "shorten", parameters)
            
            if result is None:
                logger.error("AI shorten transformation failed")
                return False
            
            logger.info("Replacing selected text with shortened version")
            return self._replace_selection(result)
            
        except Exception as e:
            logger.error(f"Failed to shorten selection: {e}")
            return False

    def _convert_to_bullets(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for convert_to_bullets action")
                return False
            
            logger.info("Getting selected text for bullet conversion")
            selected_text = self._get_selected_text()
            if not selected_text or not selected_text.strip():
                logger.warning("No text selected for bullet conversion")
                return False
            
            logger.info("Starting AI bullet conversion transformation")
            result = self.llm_client.transform_text(selected_text, "bullets", parameters)
            
            if result is None:
                logger.error("AI bullet conversion transformation failed")
                return False
            
            logger.info("Replacing selected text with bullet points")
            return self._replace_selection(result)
            
        except Exception as e:
            logger.error(f"Failed to convert text to bullets: {e}")
            return False

    def _convert_to_paragraph(self, parameters: Dict[str, Any] = None) -> bool:
        try:
            if not self.llm_client:
                logger.error("LLMClient not available for convert_to_paragraph action")
                return False
            
            logger.info("Getting selected text for paragraph conversion")
            selected_text = self._get_selected_text()
            if not selected_text or not selected_text.strip():
                logger.warning("No text selected for paragraph conversion")
                return False
            
            logger.info("Starting AI paragraph conversion transformation")
            result = self.llm_client.transform_text(selected_text, "paragraph", parameters)
            
            if result is None:
                logger.error("AI paragraph conversion transformation failed")
                return False
            
            logger.info("Replacing selected text with paragraph")
            return self._replace_selection(result)
            
        except Exception as e:
            logger.error(f"Failed to convert text to paragraph: {e}")
            return False


if __name__ == "__main__":
    print("Testing WordController")
    print("=" * 60)
    
    from llm.llm_client import LLMClient
    
    llm_client = LLMClient()
    controller = WordController(llm_client=llm_client)
    
    print(f"Supported actions: {controller.supported_actions()}")
    print("-" * 40)
    
    print("Test: Create document")
    result = controller.execute("create_document")
    print(f"Result: {result}")
    
    print("Test: Create new document (alias)")
    result = controller.execute("create_new")
    print(f"Result: {result}")
    
    print("Test: Insert text")
    result = controller.execute("insert_text", parameters={"text": "This is a test document created by Mimi. It needs to be improved. The grammar is not great and it could be more professional."})
    print(f"Result: {result}")
    
    print("Test: Select all")
    result = controller.execute("select_all")
    print(f"Result: {result}")
    
    print("Test: Rewrite selection (AI action)")
    result = controller.execute("rewrite", parameters={"tone": "professional"})
    print(f"Result: {result}")
    
    print("Test: Save document")
    result = controller.execute("save_document")
    print(f"Result: {result}")
    
    print("Test: Close document")
    result = controller.execute("close_document")
    print(f"Result: {result}")
    
    print("\nTest completed")