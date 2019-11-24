from math import log2, ceil


class RequestCode(object):
    GET = 0b00000001
    POST = 0b00000010

class ResponseCode(object):
    """ Section 12.1.2 - Pg. 87 """
    # Empty Code
    EMPTY = 0b00000000

    # Code 2 (Success)
    CREATED = 0b01000001
    DELETED = 0b01000010
    VALID = 0b01000011
    CHANGED = 0b01000100
    CONTENT = 0b01000101

    # Code 4 (Client Error)
    BAD_REQUEST = 0b10000000
    UNAUTHORIZED = 0b10000001
    BAD_OPTION = 0b10000010
    FORBIDDEN = 0b10000011
    NOT_FOUND = 0b10000100
    METHOD_NOT_ALLOWED = 0b10000101
    NOT_ACCEPTABLE = 0b10000110
    PRECONDITION_FAILED = 0b10001100
    REQUEST_ENTITY_TOO_LARGE = 0b10001101
    UNSUPPORTED_CONTENT_FORMAT = 0b10001111

    # Code 5 (Server Error)
    INTERNAL_SERVER_ERROR = 0b10100000
    NOT_IMPLEMENTED = 0b10100001
    BAD_GATEWAY = 0b10100010
    SERVICE_UNAVAILABLE = 0b10100011
    GATEWAY_TIMEOUT = 0b10100100
    PROXYING_NOT_SUPPORTED = 0b10100101


class MessageType(object):
    CONFIRMABLE = 0
    NON_CONFIRMABLE = 1
    ACK = 2
    RESET = 3


class MessageOptions(object):
    """RFC 7252 PG 89"""

    IF_MATCH = 1
    URI_HOST = 3
    E_TAG = 4
    IF_NONE_MATCH = 5
    URI_PORT = 7
    LOCATION_PATH = 8
    URI_PATH = 11
    CONTENT_FORMAT = 12
    MAX_AGE = 14
    URI_QUERY = 15
    ACCEPT = 17
    LOCATION_QUERY = 20
    PROXY_URI = 35
    PROXY_SCHEME = 39
    SIZE1 = 60


class BasicMessage(object):
    """
    Basic massage has the following format and fields:

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |Ver| T |  TKL  |      Code     |          Message ID           |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |   Token (if any, TKL bytes) ...
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    Version (Ver):  2-bit unsigned integer.  Indicates the CoAP version
      number.  Implementations of this specification MUST set this field
      to 1 (01 binary).  Other values are reserved for future versions.
      Messages with unknown version numbers MUST be silently ignored.

    Type (T):  2-bit unsigned integer.  Indicates if this message is of
        type Confirmable (0), Non-confirmable (1), Acknowledgement (2), or
        Reset (3).  The semantics of these message types are defined in
        Section 4.

    Token Length (TKL):  4-bit unsigned integer.  Indicates the length of
        the variable-length Token field (0-8 bytes).  Lengths 9-15 are
        reserved, MUST NOT be sent, and MUST be processed as a message
        format error.

    Code:  8-bit unsigned integer, split into a 3-bit class (most
        significant bits) and a 5-bit detail (least significant bits),
        documented as "c.dd" where "c" is a digit from 0 to 7 for the
        3-bit subfield and "dd" are two digits from 00 to 31 for the 5-bit
        subfield.  The class can indicate a request (0), a success
        response (2), a client error response (4), or a server error
        response (5).  (All other class values are reserved.)  As a
        special case, Code 0.00 indicates an Empty message.  In case of a
        request, the Code field indicates the Request Method; in case of a
        response, a Response Code.  Possible values are maintained in the
        CoAP Code Registries (Section 12.1).  The semantics of requests
        and responses are defined in Section 5.

    Message ID:  16-bit unsigned integer in network byte order.  Used to
        detect message duplication and to match messages of type
        Acknowledgement/Reset to messages of type Confirmable/Non-
        confirmable.  The rules for generating a Message ID and matching
        messages are defined in Section 4.

    """

    def __init__(self, typeMessage: int = 0, token: int = 0, code: int = 0, messageId: int = 0):
        self.VERSION = 1
        self.TKL = 4  # Tamanho do Token fixo por enquanto (4 bytes)
        self.typeMessage = typeMessage
        self.token = token
        self.code = code
        self.messageId = messageId

    def getVersion(self) -> int:
        return self.VERSION

    def setMessageType(self, typeMessage: int):
        self.typeMessage = typeMessage

    def getMessageType(self) -> int:
        return self.typeMessage

    def setToken(self, token: int):
        if len(str(token)) > self.TKL:
            raise Exception("Token maior que %d bytes" % self.TKL)

        self.token = token

    def getToken(self) -> int:
        return self.token

    def getTokenBytes(self) -> bytes:
        return self.token.to_bytes(self.TKL, byteorder='big')

    def setCode(self, code: int):
        self.code = code

    def getCode(self) -> int:
        return self.code

    def getCodeClass(self) -> int:
        return self.code >> 5

    def getCodeDetail(self) -> int:
        return self.code & 0x1F

    def setMessageId(self, messageId: int):
        self.messageId = messageId

    def getMessageId(self) -> int:
        return self.messageId

    def getHeader(self) -> bytes:
        header = self.VERSION << 30
        header += self.typeMessage << 28
        header += self.TKL << 24
        header += self.code << 16
        header += self.messageId
        return header.to_bytes(4, byteorder='big')


class Request(BasicMessage):
    """
    Request Message includes Options field.

        0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |   Options (if any) ...
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

    def __init__(self, typeMessage: int = 0, token: int = 0, code: int = 0, messageId: int = 0):
        """
        Atributo options vai salvar as opções no seguinte formato:
        { option1 : (length, value), option2 : (length, value) }
        Exemplo: { 3 : (9, localhost), 7 : (2, 5683) }
        """
        self.options = {}
        super(Request, self).__init__(typeMessage, token, code, messageId)

    def setOption(self, option: int, value: int or str or bytes):
        length = 0
        if isinstance(value, int):
            length = ceil(log2(5683) / 8)
        else:
            length = len(value)

        self.options[option] = (length, value)

    def getOptionsDict(self) -> dict:
        return self.options

    def getOptions(self) -> bytes:
        last_option = 0
        options = bytes()
        for key in sorted(self.options.keys()):
            option = self.options[key]
            delta = key - last_option
            option_header = delta << 4
            option_header += option[0]  # length
            option_value = option[1]

            options += option_header.to_bytes(1, byteorder='big')
            if isinstance(option_value, str):
                options += option_value.encode('utf-8')
            elif isinstance(option_value, int):
                options += option_value.to_bytes(option[0], byteorder='big')

            last_option = key

        return options


class GET(Request):
    def __init__(self, typeMessage: int = 0, token: int = 0, messageId: int = 0, code: int = None):

        # Se code não é None, o programa recebeu um pacote e está tentando identificá-lo
        if code is not None and code != RequestCode.GET:
            raise InvalidMessageCode("This is not a GET message")

        super(GET, self).__init__(typeMessage, token, RequestCode.GET, messageId)

    def getMessage(self) -> bytes:
        return self.getHeader() + self.getTokenBytes() + self.getOptions()


class POST(Request):
    def __init__(self, typeMessage: int = 0, token: int = 0, messageId: int = 0, payload: bytes = None, code: int = None):

        # Se code não é None, o programa recebeu um pacote e está tentando identificá-lo
        if code is not None and code != RequestCode.POST:
            raise InvalidMessageCode("This is not a POST message")

        self.payload = payload if payload is not None else bytes()
        super(POST, self).__init__(typeMessage, token, RequestCode.POST, messageId)

    def getPayload(self) -> bytes:
        return self.payload

    def setPayload(self, payload: bytes):
        self.payload = payload

    def getEndOptions(self) -> bytes:
        return 0xFF.to_bytes(1, byteorder='big')

    def getMessage(self) -> bytes:
        return self.getHeader() + self.getTokenBytes() + self.getOptions() + self.getEndOptions() + self.payload


class Response(BasicMessage):
    """
    Request Message includes Options field.
    The difference between a Request and a Response is on MessageCodeClass.

        0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |   Options (if any) ...
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

    def __init__(self, typeMessage: int = 0, token: int = 0, messageId: int = 0, payload: bytes = None, code: int = None):
        # Se code não é None, o programa recebeu um pacote e está tentando identifica-lo
        # Codes menores que 0b00100000 (0x20) nao sao response
        if code is not None and code < 0x20:
            raise InvalidMessageCode("This is not a Response message")

        self.payload = payload
        super(Response, self).__init__(typeMessage, token, code, messageId)

    def setPayload(self, payload: bytes):
        self.payload = payload

    def getPayload(self) -> bytes:
        return self.payload


class MessageTranslator(object):
    def __init__(self, message: bytes):
        self.message = message

    def translateResp(self) -> BasicMessage:
        if self.message is None:
            return None

        first_byte = self.message[0]
        # version = (first_byte >> 6) & 3
        type = (first_byte >> 4) & 3
        tkl = first_byte & 15

        code = self.message[1]
        messageId = int.from_bytes(self.message[2:4], byteorder="big")
        if (tkl > 0):
            end_token = 4 + tkl
            token = int.from_bytes(self.message[4:end_token], byteorder="big")
        else:
            token = 0

        msg = None
        try:
            msg = Response(typeMessage=type, token=token, messageId=messageId, code=code)
            if (token != 0) and (len(self.message) > (end_token + 1)):
                msg.setPayload(self.message[end_token+1:])
        except InvalidMessageKind as e:
            pass

        # TODO fazer para mensagens GET e POST também

        return msg


class InvalidMessageKind(Exception):
    pass

class InvalidMessageCode(InvalidMessageKind):
    pass

class InvalidMessageType(InvalidMessageKind):
    pass