from app.models.quotation_requests.rfq import RFQStatus


VALID_RFQ_TRANSITIONS = {
    RFQStatus.DRAFT: {
        RFQStatus.ISSUED,
        RFQStatus.CANCELLED,
    },

    RFQStatus.ISSUED: {
        RFQStatus.CLOSED,
        RFQStatus.CANCELLED,
    },

    RFQStatus.CLOSED: set(),

    RFQStatus.CANCELLED: set(),
}