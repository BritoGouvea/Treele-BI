class Enterprise:

    def __init__(self, id, name, commercialName, cnpj, type, adress, creationDate, modificationDate, createdBy, modifiedBy, companyId, companyName, costDatabaseId, costDatabaseDescription, buildingTypeId, buildingTypeDescription, enterpriseObservation):
        self.id = id
        self.name = name
        self.commercialName = commercialName
        self.cnpj = cnpj
        self.type = type
        self.adress = adress
        self.creationDate = creationDate
        self.modificationDate = modificationDate
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        self.companyId = companyId
        self.companyName = companyName
        self.costDatabaseId = costDatabaseId
        self.costDatabaseDescription = costDatabaseDescription
        self.buildingTypeId = buildingTypeId
        self.buildingTypeDescription = buildingTypeDescription
        self.enterpriseObservation = enterpriseObservation

class PurchaseOrder:

    def __init__(self, id, formattedPurchaseOrderId, status, consistent, authorized, disapproved,deliveryLate, supplierId, buildingId, buyerId, date, salesRepresentativeId, internalNotes, costCenterId, departamentId, companyBillId, transporterId, forecastDocumentId, forecastBillId, indexerId, discount, increase, totalAmount, directBillingDocumentId, directBillingContractNumber, directBillingJustificationId, createdBy, createdAt, modifiedBy, modifiedAt, authorizedAt, sentDate) -> None:
        self.id = id
        self.formattedPurchaseOrderId = formattedPurchaseOrderId
        self.status = status
        self.consistent = consistent
        self.authorized = authorized
        self.disapproved = disapproved
        self.deliveryLate = deliveryLate
        self.supplierId = supplierId
        self.buildingId = buildingId
        self.buyerId = buyerId
        self.date = date
        self.salesRepresentativeId = salesRepresentativeId
        self.internalNotes = internalNotes
        self.costCenterId = costCenterId
        self.departamentId = departamentId
        self.companyBillId = companyBillId
        self.transporterId = transporterId
        self.forecastDocumentId = forecastDocumentId
        self.forecastBillId = forecastBillId
        self.indexerId = indexerId
        self.discount = discount
        self.increase = increase
        self.totalAmount = totalAmount
        self.directBillingDocumentId = directBillingDocumentId
        self.directBillingContractNumber = directBillingContractNumber
        self.directBillingJustificationId = directBillingJustificationId
        self.createdBy = createdBy
        self.createdAt = createdAt
        self.modifiedBy = modifiedBy
        self.modifiedAt = modifiedAt
        self.authorizedAt = authorizedAt
        self.sentDate = sentDate
