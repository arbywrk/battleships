from domain.board import BoardMatrix, CellValue
from domain.symbol import Symbols


class BoardRenderer:
    @staticmethod
    def side_by_side(left: str, right: str, separator: str = " | ") -> str:
        left_lines = left.splitlines()
        right_lines = right.splitlines()
        height = max(len(left_lines), len(right_lines))
        left_width = max((BoardRenderer.__display_width(line) for line in left_lines), default=0)

        left_lines += [""] * (height - len(left_lines))
        right_lines += [""] * (height - len(right_lines))

        return "\n".join(
            f"{left_line}{' ' * (left_width - BoardRenderer.__display_width(left_line))}{separator}{right_line}"
            for left_line, right_line in zip(left_lines, right_lines)
        )

    @staticmethod
    def grid(top_left: str, top_right: str, bottom_left: str, bottom_right: str) -> str:
        top = BoardRenderer.side_by_side(top_left, top_right)
        bottom = BoardRenderer.side_by_side(bottom_left, bottom_right)
        return f"{top}\n\n{bottom}"

    @staticmethod
    def printable_board(
        board_matrix: BoardMatrix,
        symbols: Symbols,
        title: str = "",
        overlay: dict[tuple[int, int], str] | None = None,
        compact: bool = False,
    ) -> str:
        size = len(board_matrix)
        overlay = overlay or {}
        overlay_width = max((Symbols.symbol_width(symbol) for symbol in overlay.values()), default=0)
        cell_width = max(symbols.max_symbol_width, len(str(size)), overlay_width)
        row_label_width = len(str(size))

        lines = []
        if title:
            lines.append(title)

        cell_padding = 0 if compact else 2
        left_padding = "" if compact else " "
        right_padding = "" if compact else " "

        header_cells = [f"{left_padding}{i:>{cell_width}}{right_padding}" for i in range(1, size + 1)]
        header = " " * (row_label_width + 1) + "|" + "|".join(header_cells) + "|"
        border = "-" * (row_label_width + 1) + "+" + "+".join("-" * (cell_width + cell_padding) for _ in range(size)) + "+"
        lines.append(header)
        lines.append(border)

        for row_idx, row in enumerate(board_matrix):
            cells = []
            for col_idx, cell in enumerate(row):
                symbol = overlay.get((row_idx, col_idx))
                if symbol is None:
                    symbol = BoardRenderer.__cell_symbol(cell, symbols)
                symbol += " " * (cell_width - Symbols.symbol_width(symbol))
                cells.append(f"{left_padding}{symbol}{right_padding}")
            lines.append(f"{row_idx + 1:>{row_label_width}} |" + "|".join(cells) + "|")
            lines.append(border)

        return "\n".join(lines)

    @staticmethod
    def __cell_symbol(cell: CellValue, symbols: Symbols) -> str:
        if cell == CellValue.EMPTY:
            return symbols.empty
        if cell == CellValue.SHIP:
            return symbols.ship
        if cell == CellValue.HIT:
            return symbols.hit
        return symbols.miss

    @staticmethod
    def __display_width(text: str) -> int:
        return sum(Symbols.symbol_width(ch) for ch in text)
