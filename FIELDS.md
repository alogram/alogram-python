# Field Reference
# EntityIds
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **tenantId** | **String** | Canonical ID for the paying organization (Tenant). Opaque, immutable, lowercase.  Must start with \&quot;tid_\&quot;. Do not use domains or emails here. For a tenant&#39;s domain,  use a separate field (e.g., tenantDomain).  | [optional] [default to null] |
| **clientId** | **String** | Canonical ID for the Tenant’s business customer (e.g., merchant/partner).  Opaque, immutable, lowercase. Must start with &#39;cid_&#39;.  | [optional] [default to null] |
| **endCustomerId** | **String** | Canonical ID for the client’s end user / consumer (account holder).  Opaque, immutable, lowercase. Must start with \&quot;ecid_\&quot;.  Do not put PII (like emails or phone numbers) in this field.  | [optional] [default to null] |
| **memberId** | **String** | Canonical ID for a Tenant member/operator (employee/contractor) using the platform.  Opaque, immutable, lowercase. Must start with &#39;mid_&#39;.  | [optional] [default to null] |
| **paymentInstrumentId** | **String** | Tokenized instrument ID (non-PCI). | [optional] [default to null] |
| **deviceId** | **String** | Server-issued stable device token (device-level identifier). Should persist across sessions and logins on the same browser/device.  | [optional] [default to null] |
| **sessionId** | **String** | Application/user session identifier (login or checkout session). Typically rotates more frequently than deviceId and may be tied to authentication.  | [optional] [default to null] |
| **emailHash** | **String** | Normalized+lowercased email hash (e.g., sha256). | [optional] [default to null] |
| **emailDomainHash** | **String** | Normalized+lowercased email *domain* hash (e.g., sha256). | [optional] [default to null] |
| **phoneHash** | **String** | Normalized+lowercased phone hash (e.g., sha256). | [optional] [default to null] |
| **shippingAddressHash** | **String** | Normalized+lowercased shipping address hash (e.g., sha256). | [optional] [default to null] |
| **billingAddressHash** | **String** | Normalized+lowercased billing address hash (e.g., sha256). | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

# Purchase
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **locationId** | **String** | Unique identifier for the location where the transaction occurred. | [optional] [default to null] |
| **deviceInfo** | [**DeviceInfo**](DeviceInfo.md) |  | [optional] [default to null] |
| **timestamp** | **String** | RFC 3339 timestamp with timezone. | [optional] [default to null] |
| **transactionId** | **String** | A unique identifier for the transaction. Must be between 3 and 50 characters and only contain alphanumeric characters, underscores, or hyphens.  | [optional] [default to null] |
| **amount** | **Float** | Value of the purchase in the specified currency. Must be a positive number with up to two decimal places.  | [default to null] |
| **currency** | **String** | ISO 4217 currency code (e.g., &#39;USD&#39;). | [default to null] |
| **channel** | [**ChannelEnum**](ChannelEnum.md) |  | [optional] [default to null] |
| **entryMethod** | [**EntryMethodEnum**](EntryMethodEnum.md) |  | [optional] [default to null] |
| **paymentMethod** | [**PaymentMethod**](PaymentMethod.md) |  | [default to null] |
| **order** | [**OrderContext**](OrderContext.md) |  | [optional] [default to null] |
| **discounts** | [**List**](DiscountCode.md) | List of discount codes applied to the purchase. | [optional] [default to null] |
| **payerType** | [**PayerTypeEnum**](PayerTypeEnum.md) |  | [optional] [default to null] |
| **storedCredential** | [**StoredCredentialContext**](StoredCredentialContext.md) |  | [optional] [default to null] |
| **merchant** | [**MerchantContext**](MerchantContext.md) |  | [optional] [default to null] |
| **metadata** | **String** | Optional key-value pairs providing additional context for the request.  Each key should be descriptive, and values should not exceed 2048 characters.  Each key should be descriptive.  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

# PaymentEvent
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **paymentIntentId** | **String** | Server-minted unique payment identifier. | [default to null] |
| **eventType** | [**PaymentEventType**](PaymentEventType.md) |  | [default to null] |
| **timestamp** | **String** | RFC 3339 timestamp with timezone. | [default to null] |
| **amount** | **Float** | Value of the purchase in the specified currency. Must be a positive number with up to two decimal places.  | [optional] [default to null] |
| **currency** | **String** | ISO 4217 currency code (e.g., &#39;USD&#39;). | [optional] [default to null] |
| **outcome** | [**PaymentOutcome**](PaymentOutcome.md) |  | [optional] [default to null] |
| **metadata** | **String** | Optional key-value pairs providing additional context for the request.  Each key should be descriptive, and values should not exceed 2048 characters.  Each key should be descriptive.  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
