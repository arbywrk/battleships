from domain.board import BoardMatrix, CellValue
from domain.symbol import Symbols


class BoardRenderer:
    @staticmethod
    def printable_board(
        board_matrix: BoardMatrix,
        symbols: Symbols,
        title: str = "",
        overlay: dict[tuple[int, int], str] | None = None,
    ) -> str:
        size = len(board_matrix)
        overlay = overlay or {}
        overlay_width = max((Symbols.symbol_width(symbol) for symbol in overlay.values()), default=0)
        cell_width = max(symbols.max_symbol_width, len(str(size - 1)), overlay_width)
        row_label_width = len(str(size - 1))

        lines = []
        if title:
            lines.append(title)

        header_cells = [f" {i:>{cell_width}} " for i in range(size)]
        header = " " * (row_label_width + 1) + "|" + "|".join(header_cells) + "|"
        border = "-" * (row_label_width + 1) + "+" + "+".join("-" * (cell_width + 2) for _ in range(size)) + "+"
        lines.append(header)
        lines.append(border)

        for row_idx, row in enumerate(board_matrix):
            cells = []
            for col_idx, cell in enumerate(row):
                symbol = overlay.get((row_idx, col_idx))
                if symbol is None:
                    symbol = BoardRenderer.__cell_symbol(cell, symbols)
                symbol += " " * (cell_width - Symbols.symbol_width(symbol))
                cells.append(f" {symbol} ")
            lines.append(f"{row_idx:>{row_label_width}} |" + "|".join(cells) + "|")
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
