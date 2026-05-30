from domain.board import BoardMatrix, CellValue
from domain.symbol import Symbols


BoardOverlay = dict[tuple[int, int], str]


class BoardRenderer:
    """Turns board matrices into text that can be printed in the terminal."""

    @staticmethod
    def printable_board(
        board_matrix: BoardMatrix,
        symbols: Symbols,
        title: str = "",
        overlay: BoardOverlay | None = None,
        compact: bool = False,
    ) -> str:
        """
        Build one printable board.

        The game stores row and column indexes from 0, but the UI displays
        them from 1 because that is easier for players to read.
        """
        board_size: int = len(board_matrix)
        board_overlay: BoardOverlay = overlay or {}
        cell_width: int = BoardRenderer.__cell_width(board_size, symbols, board_overlay)
        row_label_width: int = len(str(board_size))
        left_padding: str = "" if compact else " "
        right_padding: str = "" if compact else " "

        lines: list[str] = []
        if title:
            lines.append(title)

        lines.append(BoardRenderer.__header_line(board_size, cell_width, row_label_width, left_padding, right_padding))
        lines.append(BoardRenderer.__border_line(board_size, cell_width, row_label_width, compact))

        for row_index, row in enumerate(board_matrix):
            lines.append(BoardRenderer.__row_line(
                row_index,
                row,
                symbols,
                board_overlay,
                cell_width,
                row_label_width,
                left_padding,
                right_padding,
            ))
            lines.append(BoardRenderer.__border_line(board_size, cell_width, row_label_width, compact))

        return "\n".join(lines)

    @staticmethod
    def side_by_side(left_text: str, right_text: str, separator: str = " | ") -> str:
        """Place two multi-line text blocks next to each other."""
        left_lines: list[str] = left_text.splitlines()
        right_lines: list[str] = right_text.splitlines()
        total_lines: int = max(len(left_lines), len(right_lines))
        left_width: int = max((BoardRenderer.__display_width(line) for line in left_lines), default=0)

        left_lines += [""] * (total_lines - len(left_lines))
        right_lines += [""] * (total_lines - len(right_lines))

        combined_lines: list[str] = []
        for left_line, right_line in zip(left_lines, right_lines):
            missing_spaces: int = left_width - BoardRenderer.__display_width(left_line)
            combined_lines.append(f"{left_line}{' ' * missing_spaces}{separator}{right_line}")

        return "\n".join(combined_lines)

    @staticmethod
    def grid(top_left: str, top_right: str, bottom_left: str, bottom_right: str) -> str:
        """Place four text blocks in a two-by-two grid."""
        top_row: str = BoardRenderer.side_by_side(top_left, top_right)
        bottom_row: str = BoardRenderer.side_by_side(bottom_left, bottom_right)
        return f"{top_row}\n\n{bottom_row}"

    @staticmethod
    def __header_line(
        board_size: int,
        cell_width: int,
        row_label_width: int,
        left_padding: str,
        right_padding: str,
    ) -> str:
        column_labels: list[str] = []
        for column_number in range(1, board_size + 1):
            column_labels.append(f"{left_padding}{column_number:>{cell_width}}{right_padding}")
        return " " * (row_label_width + 1) + "|" + "|".join(column_labels) + "|"

    @staticmethod
    def __border_line(board_size: int, cell_width: int, row_label_width: int, compact: bool) -> str:
        extra_padding_width: int = 0 if compact else 2
        cell_border: str = "-" * (cell_width + extra_padding_width)
        return "-" * (row_label_width + 1) + "+" + "+".join(cell_border for _cell in range(board_size)) + "+"

    @staticmethod
    def __row_line(
        row_index: int,
        row: list[CellValue],
        symbols: Symbols,
        overlay: BoardOverlay,
        cell_width: int,
        row_label_width: int,
        left_padding: str,
        right_padding: str,
    ) -> str:
        cell_texts: list[str] = []
        for column_index, cell_value in enumerate(row):
            board_position: tuple[int, int] = (row_index, column_index)
            if board_position in overlay:
                cell_symbol: str = overlay[board_position]
            else:
                cell_symbol = BoardRenderer.__cell_symbol(cell_value, symbols)

            cell_symbol += " " * (cell_width - Symbols.symbol_width(cell_symbol))
            cell_texts.append(f"{left_padding}{cell_symbol}{right_padding}")

        displayed_row_number: int = row_index + 1
        return f"{displayed_row_number:>{row_label_width}} |" + "|".join(cell_texts) + "|"

    @staticmethod
    def __cell_width(board_size: int, symbols: Symbols, overlay: BoardOverlay) -> int:
        overlay_width: int = max((Symbols.symbol_width(symbol) for symbol in overlay.values()), default=0)
        return max(symbols.max_symbol_width, len(str(board_size)), overlay_width)

    @staticmethod
    def __cell_symbol(cell_value: CellValue, symbols: Symbols) -> str:
        if cell_value == CellValue.EMPTY:
            return symbols.empty
        if cell_value == CellValue.SHIP:
            return symbols.ship
        if cell_value == CellValue.HIT:
            return symbols.hit
        return symbols.miss

    @staticmethod
    def __display_width(text: str) -> int:
        """Return terminal display width, with emoji counted as wider."""
        total_width: int = 0
        for character in text:
            total_width += Symbols.symbol_width(character)
        return total_width
