import pytest

def test_initial_menu_items_structure_and_categories():
    from src.seed_data import INITIAL_MENU_ITEMS
    assert len(INITIAL_MENU_ITEMS) >= 15
    categories = {item["kategori"] for item in INITIAL_MENU_ITEMS}
    expected_categories = {"Ayam Kampung", "Ayam Negri", "Ikan", "Daging Sapi", "Ayam Fillet", "Menu Favorit"}
    assert expected_categories.issubset(categories)

    for item in INITIAL_MENU_ITEMS:
        assert "id_menu" in item
        assert "kategori" in item
        assert "nama_item" in item
        assert "porsi_varian" in item
        assert "harga" in item
        assert isinstance(item["harga"], (int, float))
        assert item["harga"] > 0
        assert "is_promo" in item
        assert "is_active" in item
