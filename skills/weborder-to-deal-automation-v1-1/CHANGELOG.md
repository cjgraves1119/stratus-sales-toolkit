# Changelog

## v1-1 (2025-12-10)

### Added
- **Cisco Rep Auto-Assignment**: Automatically searches Gmail for deal approval emails to identify Cisco reps
- **Meraki_ISRs Lookup**: Validates Cisco rep emails against the Meraki_ISRs module
- **Smart Assignment Logic**:
  - 0 reps found → Keep Stratus Sales default
  - 1 rep found → Auto-assign to deal
  - 2+ reps found → Flag for user clarification
- **Amount Field**: Now includes Grand_Total from Sales_Order in deal creation
- **Enhanced Summary Table**: Shows assigned Cisco rep for each deal

### Changed
- Updated description to reflect Cisco rep assignment capability
- Expanded summary output to include Cisco Rep column
- Added Gmail search step to core workflow

### Fixed
- N/A (initial feature addition)

---

## v1-0 (Initial Release)

- Basic WebOrder to Deal automation
- Account lookup from Sales_Orders
- Deal creation with standard fields
- Bidirectional PO-Deal linking
- Stratus Sales as default Meraki_ISR
