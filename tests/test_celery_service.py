import io
import pytest
from PIL import Image
from unittest.mock import patch, MagicMock
from app.services.celery_service import process_page, save_translated_texts


@pytest.fixture
def sample_pdf():
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\n"
        b"endobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\n"
        b"endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000100 00000 n \n"
        b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n150\n%%EOF"
    )
    return io.BytesIO(pdf_content)


@pytest.fixture
def mock_minio_client():
    with patch("app.services.celery_service.minio_client") as mock:
        yield mock


@pytest.fixture
def mock_pytesseract():
    with patch("app.services.celery_service.pytesseract") as mock:
        yield mock


@pytest.fixture
def mock_google_translator():
    with patch("app.services.celery_service.GoogleTranslator") as mock:
        instance = mock.return_value
        instance.translate.return_value = "Переведенный текст"
        yield mock


@patch("app.services.celery_service.tempfile.NamedTemporaryFile")
@patch("app.services.celery_service.fitz.open")
def test_process_page(mock_fitz_open, mock_tempfile, mock_minio_client, mock_pytesseract, mock_google_translator, sample_pdf):
    mock_temp_file = MagicMock()
    mock_temp_file.name = "tempfile.pdf"
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file

    mock_pdf_document = MagicMock()
    mock_fitz_open.return_value.__enter__.return_value = mock_pdf_document
    mock_page = MagicMock()
    mock_pdf_document.load_page.return_value = mock_page

    mock_pixmap = MagicMock()
    mock_page.get_pixmap.return_value = mock_pixmap
    mock_pixmap.tobytes.return_value = b"fakeimagebytes"

    with patch("PIL.Image.open", return_value=Image.new('RGB', (100, 100))) as mock_image_open:
        result = process_page("test.pdf", "ru")

    assert result == "Переведенный текст"
    mock_minio_client.fget_object.assert_called_once()
    mock_pdf_document.load_page.assert_called_once_with(0)
    mock_google_translator.return_value.translate.assert_called_once()


def test_save_translated_texts(mock_minio_client):
    texts = ["Translated Text 1", "Translated Text 2"]

    save_translated_texts(texts)

    mock_minio_client.fput_object.assert_called_once()
