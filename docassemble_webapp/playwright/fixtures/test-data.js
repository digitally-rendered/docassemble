/**
 * Test data fixtures for Ontario Family Law Forms Wizard tests
 * Contains predefined scenarios for different user paths through the wizard
 */

const testScenarios = {
  // Emergency Scenarios
  emergency: {
    // Emergency -> Married -> Seeking divorce only
    emergencyDivorceOnly: {
      emergency_situation: true,
      relationship_status: 'married',
      orders: {
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      },
      divorce_complexity: 'uncontested',
      children_involved: false,
      expected_forms: [
        'Form 8 - Application (General)',
        'Form 14 - Notice of Motion',
        'Form 14A - Supporting Affidavit'
      ],
      expected_timeline: 'Immediate filing',
      expected_court: 'Superior Court of Justice'
    },

    // Emergency -> Married -> Seeking divorce + custody + support
    emergencyDivorceMultiple: {
      emergency_situation: true,
      relationship_status: 'married',
      orders: {
        divorce: true,
        custody: true,
        child_support: true,
        spousal_support: true,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      },
      financial_data: {
        property_value: 50000,
        support_involved: true,
        business_owner: false,
        pension_involved: false
      },
      expected_forms: [
        'Form 8 - Application (General)',
        'Form 14 - Notice of Motion',
        'Form 14A - Supporting Affidavit',
        'Form 13 - Financial Statement (Support Claims)',
        'Form 13A - Certificate of Financial Disclosure',
        'Form 35.1 - Affidavit (Custody/Access)'
      ],
      expected_timeline: 'Immediate filing',
      expected_court: 'Superior Court of Justice'
    },

    // Emergency -> Common-law -> Multiple issues
    emergencyCommonLawMultiple: {
      emergency_situation: true,
      relationship_status: 'common_law',
      orders: {
        divorce: false,
        custody: true,
        child_support: true,
        spousal_support: true,
        property: true,
        exclusive_possession: true,
        restraining_order: false,
        enforcement: false,
        other: false
      },
      financial_data: {
        property_value: 100000,
        support_involved: true,
        business_owner: false,
        pension_involved: true
      },
      expected_forms: [
        'Form 8 - Application (General)',
        'Form 14 - Notice of Motion',
        'Form 14A - Supporting Affidavit',
        'Form 13.1 - Financial Statement (Property & Support)',
        'Form 13A - Certificate of Financial Disclosure',
        'Form 35.1 - Affidavit (Custody/Access)'
      ],
      expected_timeline: 'Immediate filing',
      expected_court: 'Superior Court of Justice'
    },

    // Emergency -> Never lived together -> Child support + custody
    emergencyNeverTogether: {
      emergency_situation: true,
      relationship_status: 'never_together',
      orders: {
        custody: true,
        child_support: true,
        paternity: false,
        restraining_order: false,
        other: false
      },
      financial_data: {
        property_value: 25000,
        support_involved: true,
        business_owner: false,
        pension_involved: false
      },
      expected_forms: [
        'Form 8 - Application (General)',
        'Form 14 - Notice of Motion',
        'Form 14A - Supporting Affidavit',
        'Form 13 - Financial Statement (Support Claims)',
        'Form 13A - Certificate of Financial Disclosure',
        'Form 35.1 - Affidavit (Custody/Access)'
      ],
      expected_timeline: 'Immediate filing',
      expected_court: 'Ontario Court of Justice'
    }
  },

  // Non-Emergency Married Scenarios
  married: {
    // MIP completed -> Married -> Divorce only (uncontested, no children)
    uncontestedDivorceNoChildren: {
      emergency_situation: false,
      mip_status: 'completed',
      relationship_status: 'married',
      orders: {
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      },
      divorce_complexity: 'uncontested',
      children_involved: false,
      expected_forms: [
        'Form 8A - Application (Divorce)',
        'Form 36 - Affidavit for Divorce',
        'Form 25A - Divorce Order'
      ],
      expected_timeline: '4-6 months',
      expected_court: 'Superior Court of Justice'
    },

    // MIP completed -> Married -> Divorce only (uncontested, with children)
    uncontestedDivorceWithChildren: {
      emergency_situation: false,
      mip_status: 'completed',
      relationship_status: 'married',
      orders: {
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      },
      divorce_complexity: 'uncontested',
      children_involved: true,
      expected_forms: [
        'Form 8A - Application (Divorce)',
        'Form 36 - Affidavit for Divorce',
        'Form 35.1 - Affidavit (Custody/Access)'
      ],
      expected_timeline: '12-18+ months',
      expected_court: 'Superior Court of Justice'
    },

    // MIP completed -> Married -> Divorce + other orders (becomes contested)
    divorceWithOtherOrders: {
      emergency_situation: false,
      mip_status: 'completed',
      relationship_status: 'married',
      orders: {
        divorce: true,
        custody: true,
        child_support: true,
        spousal_support: false,
        property: true,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      },
      financial_data: {
        property_value: 150000,
        support_involved: true,
        business_owner: true,
        pension_involved: true
      },
      expected_forms: [
        'Form 8A - Application (Divorce)',
        'Form 36 - Affidavit for Divorce',
        'Form 13.1 - Financial Statement (Property & Support)',
        'Form 13A - Certificate of Financial Disclosure',
        'Form 35.1 - Affidavit (Custody/Access)'
      ],
      expected_timeline: '12-18+ months',
      expected_court: 'Superior Court of Justice'
    },

    // MIP not completed -> Married -> Separation only (no divorce)
    separationOnly: {
      emergency_situation: false,
      mip_status: 'not_completed',
      relationship_status: 'married',
      orders: {
        divorce: false,
        custody: true,
        child_support: true,
        spousal_support: true,
        property: false,
        exclusive_possession: true,
        restraining_order: false,
        enforcement: false,
        other: false
      },
      financial_data: {
        property_value: 60000,
        support_involved: true,
        business_owner: false,
        pension_involved: false
      },
      expected_forms: [
        'Form 8 - Application (General)',
        'Form 13 - Financial Statement (Support Claims)',
        'Form 13A - Certificate of Financial Disclosure',
        'Form 35.1 - Affidavit (Custody/Access)'
      ],
      expected_timeline: '12-18 months',
      expected_court: 'Ontario Court of Justice'
    }
  },

  // Common-Law Scenarios
  commonLaw: {
    // Common-law -> Child custody only
    custodyOnly: {
      emergency_situation: false,
      mip_status: 'unsure',
      relationship_status: 'common_law',
      orders: {
        divorce: false,
        custody: true,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      },
      expected_forms: [
        'Form 8 - Application (General)',
        'Form 35.1 - Affidavit (Custody/Access)'
      ],
      expected_timeline: '12-18 months',
      expected_court: 'Ontario Court of Justice'
    },

    // Common-law -> Support + Property
    supportAndProperty: {
      emergency_situation: false,
      mip_status: 'completed',
      relationship_status: 'common_law',
      orders: {
        divorce: false,
        custody: false,
        child_support: false,
        spousal_support: true,
        property: true,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      },
      financial_data: {
        property_value: 80000,
        support_involved: true,
        business_owner: false,
        pension_involved: true
      },
      expected_forms: [
        'Form 8 - Application (General)',
        'Form 13.1 - Financial Statement (Property & Support)',
        'Form 13A - Certificate of Financial Disclosure'
      ],
      expected_timeline: '12-18 months',
      expected_court: 'Superior Court of Justice'
    },

    // Common-law -> All issues selected
    allIssues: {
      emergency_situation: false,
      mip_status: 'unsure',
      relationship_status: 'common_law',
      orders: {
        divorce: false,
        custody: true,
        child_support: true,
        spousal_support: true,
        property: true,
        exclusive_possession: true,
        restraining_order: true,
        enforcement: false,
        other: false
      },
      financial_data: {
        property_value: 200000,
        support_involved: true,
        business_owner: true,
        pension_involved: true
      },
      expected_forms: [
        'Form 8 - Application (General)',
        'Form 13.1 - Financial Statement (Property & Support)',
        'Form 13A - Certificate of Financial Disclosure',
        'Form 35.1 - Affidavit (Custody/Access)'
      ],
      expected_timeline: '12-18 months',
      expected_court: 'Superior Court of Justice'
    }
  },

  // Never Lived Together Scenarios
  neverTogether: {
    // Never together -> Child custody + support
    custodyAndSupport: {
      emergency_situation: false,
      mip_status: 'completed',
      relationship_status: 'never_together',
      orders: {
        custody: true,
        child_support: true,
        paternity: false,
        restraining_order: false,
        other: false
      },
      financial_data: {
        property_value: 30000,
        support_involved: true,
        business_owner: false,
        pension_involved: false
      },
      expected_forms: [
        'Form 8 - Application (General)',
        'Form 13 - Financial Statement (Support Claims)',
        'Form 13A - Certificate of Financial Disclosure',
        'Form 35.1 - Affidavit (Custody/Access)'
      ],
      expected_timeline: '12-18 months',
      expected_court: 'Ontario Court of Justice'
    },

    // Never together -> Paternity declaration
    paternityOnly: {
      emergency_situation: false,
      mip_status: 'completed',
      relationship_status: 'never_together',
      orders: {
        custody: false,
        child_support: false,
        paternity: true,
        restraining_order: false,
        other: false
      },
      expected_forms: [
        'Form 8 - Application (General)',
        'Form 34A - Affidavit of Parentage'
      ],
      expected_timeline: '12-18 months',
      expected_court: 'Ontario Court of Justice'
    },

    // Never together -> Restraining order only
    restrainingOrderOnly: {
      emergency_situation: false,
      mip_status: 'completed',
      relationship_status: 'never_together',
      orders: {
        custody: false,
        child_support: false,
        paternity: false,
        restraining_order: true,
        other: false
      },
      expected_forms: [
        'Form 8 - Application (General)'
      ],
      expected_timeline: '12-18 months',
      expected_court: 'Ontario Court of Justice'
    }
  }
};

// Financial data templates
const financialDataTemplates = {
  lowValue: {
    property_value: 25000,
    support_involved: false,
    business_owner: false,
    pension_involved: false
  },
  
  mediumValue: {
    property_value: 75000,
    support_involved: true,
    business_owner: false,
    pension_involved: false
  },
  
  highValue: {
    property_value: 150000,
    support_involved: true,
    business_owner: true,
    pension_involved: true
  },
  
  businessOwner: {
    property_value: 100000,
    support_involved: true,
    business_owner: true,
    pension_involved: false
  }
};

// Common form combinations for validation
const expectedFormCombinations = {
  divorceUncontested: ['Form 8A', 'Form 36', 'Form 25A'],
  divorceContested: ['Form 8A', 'Form 36'],
  applicationGeneral: ['Form 8'],
  withFinancialSupport: ['Form 13', 'Form 13A'],
  withFinancialProperty: ['Form 13.1', 'Form 13A'],
  withCustody: ['Form 35.1'],
  withPaternity: ['Form 34A'],
  serviceForm: ['Form 6B']
};

module.exports = {
  testScenarios,
  financialDataTemplates,
  expectedFormCombinations
};