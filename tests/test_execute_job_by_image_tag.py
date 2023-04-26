from http import HTTPStatus

from src.consts import Endpoint
from tests.conftest import image_tag_1_in_ecr


# TODO: add basic test job + test repo in ECR + get_repo() method for prod and test
# TODO: add test images to ECR test, so I won't have to test against prod ECR repo
# TODO: consider docker for testing instead of ECR test repo
def test_valid_input(test_client):
    data = {
        "image_tag": image_tag_1_in_ecr,
        "execution_parameters": {
            "source_name": "wabetainfo",
            "url": "https://wabetainfo.com/updates/?filter=1",
        },
        "executable_file_name": "main.py",
    }
    response = test_client.post(Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, json=data)
    assert response.status_code == HTTPStatus.OK
    assert response.json["error"] == ""
    assert "wabetainfo" in eval(response.json["output"])


class TestImageTag:
    data = {
        "image_tag": image_tag_1_in_ecr,
        "execution_parameters": {
            "source_name": "wabetainfo",
            "url": "https://wabetainfo.com/updates/?filter=1",
        },
        "executable_file_name": "main.py",
    }

    def test_missing_image_tag(self, test_client):
        self.data.pop("image_tag")
        response = test_client.post(
            Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, json=self.data
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "ImageTag: field required"

    def test_empty_image_tag(self, test_client):
        self.data["image_tag"] = ""
        response = test_client.post(
            Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, json=self.data
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "ImageTag: input cannot be empty"

    def test_image_tag_input_is_not_a_string(self, test_client):
        # image_tag is automatically cast to string by Pydantic
        self.data["image_tag"] = 123
        response = test_client.post(
            Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, json=self.data
        )
        assert response.status_code == HTTPStatus.OK

    def test_image_tag_does_not_exist_in_db(self, test_client):
        self.data["image_tag"] = "image_tag_not_in_db"
        response = test_client.post(
            Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, json=self.data
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == f"image_tag {self.data['image_tag']} not found in DB"


class TestExecutionParameters:
    data = {
        "image_tag": image_tag_1_in_ecr,
        "execution_parameters": {
            "source_name": "wabetainfo",
            "url": "https://wabetainfo.com/updates/?filter=1",
        },
        "executable_file_name": "main.py",
    }

    def test_missing_execution_parameters(self, test_client):
        self.data.pop("execution_parameters")
        response = test_client.post(
            Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, json=self.data
        )
        assert response.status_code == HTTPStatus.OK

    def test_empty_execution_parameters(self, test_client):
        self.data["execution_parameters"] = {}
        response = test_client.post(
            Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, json=self.data
        )
        assert response.status_code == HTTPStatus.OK


class TestExecutableFileName:
    data = {
        "image_tag": image_tag_1_in_ecr,
        "execution_parameters": {
            "source_name": "wabetainfo",
            "url": "https://wabetainfo.com/updates/?filter=1",
        },
        "executable_file_name": "main.py",
    }

    def test_missing_executable_file_name(self, test_client):
        self.data.pop("executable_file_name")
        response = test_client.post(
            Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, json=self.data
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "ExecutableFileName: field required"

    def test_empty_executable_file_name(self, test_client):
        self.data["executable_file_name"] = ""
        response = test_client.post(
            Endpoint.EXECUTE_JOB_BY_IMAGE_TAG.value, json=self.data
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.text == "ExecutableFileName: input cannot be empty"
