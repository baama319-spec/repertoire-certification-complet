from rest_framework.exceptions import APIException
class ConflitMetier(APIException):
    status_code = 409
    default_detail = "Cette opération est impossible dans l'état actuel."
