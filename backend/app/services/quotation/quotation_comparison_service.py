from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.quotation.quotation_item import QuotationItem
from app.models.quotation_requests.rfq import RFQ, RFQStatus
from app.models.quotation_requests.rfq_item import RFQItem
from app.models.quotation_requests.rfq_vendor import RFQVendor
from app.models.quotation.quotation import Quotation, QuotationStatus
from app.models.vendor.vendor import Vendor

from app.schemas.quotation.quotation_comparison_schema import (
    QuotationItemPriceResponse,
    RFQItemComparisonResponse,
    QuotationComparisonSummary,
    RFQQuotationComparisonResponse,
)


class QuotationComparisonService:

    @staticmethod
    def compare_rfq_quotations(
        db: Session,
        rfq_id: int,
    ) -> RFQQuotationComparisonResponse:

        rfq = db.query(RFQ).filter(RFQ.id == rfq_id).first()

        if rfq is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RFQ not found",
            )

        if rfq.status != RFQStatus.CLOSED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Quotations can only be compared after the RFQ is closed",
            )

        rfq_items = db.query(RFQItem).filter(RFQItem.rfq_id == rfq_id).all()

        rfq_vendors = db.query(RFQVendor).filter(RFQVendor.rfq_id == rfq_id).all()
        rfq_vendor_ids = [rv.id for rv in rfq_vendors]

        quotations = (
            db.query(Quotation)
            .filter(
                Quotation.rfq_vendor_id.in_(rfq_vendor_ids),
                Quotation.status == QuotationStatus.SUBMITTED.value,
            )
            .order_by(Quotation.total_amount.asc())
            .all()
        )

        quotation_summaries = []

        for index, quotation in enumerate(quotations, start=1):

            rfq_vendor = next(
                (rv for rv in rfq_vendors if rv.id == quotation.rfq_vendor_id),
                None
            )

            if rfq_vendor is None:
                continue

            vendor = db.query(Vendor).filter(Vendor.id == rfq_vendor.vendor_id).first()

            if vendor is None:
                continue

            summary = QuotationComparisonSummary(
                rank=index,
                quotation_id=quotation.id,
                vendor_id=vendor.id,
                vendor_name=vendor.name,
                vendor_code=vendor.vendor_code,
                total_amount=quotation.total_amount,
                currency=quotation.currency,
                delivery_days=None,
                payment_terms=None,
                validity_date=quotation.valid_until,
            )

            quotation_summaries.append(summary)

        quotation_items = (
            db.query(QuotationItem)
            .filter(QuotationItem.quotation_id.in_([q.id for q in quotations]))
            .all()
        )

        quotation_item_map = {}

        for quotation_item in quotation_items:

            rfq_item_id = quotation_item.rfq_item_id

            if rfq_item_id not in quotation_item_map:
                quotation_item_map[rfq_item_id] = []

            quotation = next(
                (q for q in quotations if q.id == quotation_item.quotation_id),
                None
            )

            if quotation is None:
                continue

            quotation_item_map[rfq_item_id].append({
                "quotation": quotation,
                "item": quotation_item,
            })

        item_comparisons = []

        for rfq_item in rfq_items:

            item_prices = []

            quotation_items_list = quotation_item_map.get(rfq_item.id, [])

            quotation_items_list.sort(key=lambda data: data["item"].total_price)

            for data in quotation_items_list:

                quotation = data["quotation"]
                quotation_item = data["item"]

                rfq_vendor = next(
                    (rv for rv in rfq_vendors if rv.id == quotation.rfq_vendor_id),
                    None
                )

                if rfq_vendor is None:
                    continue

                vendor = db.query(Vendor).filter(Vendor.id == rfq_vendor.vendor_id).first()

                if vendor is None:
                    continue

                item_price = QuotationItemPriceResponse(
                    quotation_id=quotation.id,
                    vendor_id=vendor.id,
                    vendor_name=vendor.name,
                    quantity=quotation_item.quantity,
                    unit_price=quotation_item.unit_price,
                    total_price=quotation_item.total_price,
                )

                item_prices.append(item_price)

            item_comparison = RFQItemComparisonResponse(
                rfq_item_id=rfq_item.id,
                item_name=rfq_item.item_name,
                description=rfq_item.description,
                quantity=rfq_item.quantity,
                unit=rfq_item.unit,
                prices=item_prices,
            )

            item_comparisons.append(item_comparison)

        return RFQQuotationComparisonResponse(
            rfq_id=rfq.id,
            rfq_number=rfq.rfq_number,
            title=rfq.title,
            quotation_count=len(quotations),
            quotations=quotation_summaries,
            item_comparison=item_comparisons,
        )