import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
import io


client = TestClient(app)


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
    with patch("app.api.endpoints.minio_client") as mock:
        yield mock


@pytest.fixture
def mock_chain():
    with patch("app.api.endpoints.chain") as mock:
        yield mock


@pytest.fixture
def mock_async_result(request):
    with patch("app.api.endpoints.AsyncResult") as mock:
        instance = mock.return_value
        instance.successful.return_value = request.param["successful"]
        instance.status = request.param["status"]
        yield mock


def test_upload_pdf(mock_chain, mock_minio_client, sample_pdf):
    mock_chain_instance = MagicMock()
    mock_chain_instance().id = "fake_task_id"
    mock_chain.return_value = mock_chain_instance

    response = client.post(
        "/upload-pdf/",
        files={"file": ("test.pdf", sample_pdf, "application/pdf")},
        params={"language": "ru"})

    assert response.status_code == 200, f"Response: {response.json()}"
    assert response.json()["task_id"] == "fake_task_id"


def test_file_format(sample_pdf):
    response = client.post(
        "/upload-pdf/",
        files={"file": ("test.txt", sample_pdf, "application/pdf")},
        params={"language": "ru"})

    assert response.status_code == 400
    assert response.json() == {'detail': 'The file must be in PDF format'}


def test_mime_file_type(sample_pdf):
    response = client.post(
        "/upload-pdf/",
        files={"file": ("test.pdf", sample_pdf, "text/plain")},
        params={"language": "ru"})

    assert response.status_code == 400
    assert response.json() == {'detail': 'Invalid MIME file type'}


def test_invalid_language_code(sample_pdf):
    response = client.post(
        "/upload-pdf/",
        files={"file": ("test.pdf", sample_pdf, "application/pdf")},
        params={"language": "jp"})

    assert response.status_code == 500
    assert response.json() == {'detail': 'Invalid language code'}


@pytest.mark.parametrize("mock_async_result", [{"successful": True, "status": "SUCCESS"}], indirect=True)
def test_get_task_status_success(mock_async_result, mock_minio_client):
    mock_minio_client.presigned_get_object.return_value = "http://fake-url.com/download"
    task_id = "test_task_id"
    response = client.get(f"/task-status/{task_id}")

    assert response.status_code == 200
    assert response.json() == {"download_url": "http://fake-url.com/download"}


@pytest.mark.parametrize("mock_async_result", [{"successful": False, "status": "PENDING"}], indirect=True)
def test_get_task_status_pending(mock_async_result):
    task_id = "test_task_id"
    response = client.get(f"/task-status/{task_id}")

    assert response.status_code == 202
    assert response.json() == {"status": "PENDING"}

