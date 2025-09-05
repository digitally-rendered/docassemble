/**
 * Test data fixtures for Form 13 - Financial Statement
 * Provides reusable test data for various scenarios
 */

const testScenarios = {
  // Minimal valid data to complete the form
  minimal: {
    personal: {
      fullName: 'John Smith',
      courtName: 'Superior Court of Justice',
      courtFileNumber: '12345/24'
    },
    contact: {
      address: '100 Queen Street West, Toronto, ON',
      postalCode: 'M5H 2N2',
      email: 'john.smith@example.com',
      phone: '416-555-0100'
    },
    income: [
      { 
        description: 'Employment Income', 
        amount: 5000, 
        frequency: 'monthly',
        employer: 'ABC Corporation'
      }
    ],
    expenses: [
      { 
        description: 'Rent/Mortgage', 
        amount: 2000, 
        category: 'housing',
        frequency: 'monthly'
      },
      { 
        description: 'Groceries', 
        amount: 800, 
        category: 'food',
        frequency: 'monthly'
      }
    ],
    assets: [],
    debts: [],
    signature: {
      name: 'John Smith',
      date: new Date().toISOString().split('T')[0],
      location: 'Toronto, Ontario'
    }
  },

  // Complete data with all sections filled
  complete: {
    personal: {
      fullName: 'Jane Elizabeth Doe',
      courtName: 'Superior Court of Justice',
      courtFileNumber: 'FC-24-001234',
      lawyerName: 'Sarah Counsel',
      lsoNumber: '12345A'
    },
    contact: {
      address: '456 Bay Street, Suite 1000, Toronto, ON',
      postalCode: 'M5J 2T3',
      email: 'jane.doe@email.com',
      phone: '416-555-0200',
      fax: '416-555-0201'
    },
    income: [
      { 
        description: 'Employment Income - Full Time', 
        amount: 7500, 
        frequency: 'monthly',
        employer: 'Tech Solutions Inc.'
      },
      { 
        description: 'Part-time Consulting', 
        amount: 2000, 
        frequency: 'monthly',
        employer: 'Self-employed'
      },
      { 
        description: 'Investment Income', 
        amount: 500, 
        frequency: 'monthly',
        source: 'TD Investment Portfolio'
      },
      { 
        description: 'Child Tax Benefit', 
        amount: 450, 
        frequency: 'monthly',
        source: 'Canada Revenue Agency'
      }
    ],
    expenses: [
      { description: 'Mortgage Payment', amount: 3200, category: 'housing', frequency: 'monthly' },
      { description: 'Property Tax', amount: 500, category: 'housing', frequency: 'monthly' },
      { description: 'Home Insurance', amount: 150, category: 'housing', frequency: 'monthly' },
      { description: 'Utilities (Hydro, Gas, Water)', amount: 300, category: 'housing', frequency: 'monthly' },
      { description: 'Internet & Cable', amount: 150, category: 'housing', frequency: 'monthly' },
      { description: 'Groceries', amount: 1000, category: 'food', frequency: 'monthly' },
      { description: 'Restaurants', amount: 300, category: 'food', frequency: 'monthly' },
      { description: 'Car Payment', amount: 650, category: 'transportation', frequency: 'monthly' },
      { description: 'Car Insurance', amount: 200, category: 'transportation', frequency: 'monthly' },
      { description: 'Gas', amount: 250, category: 'transportation', frequency: 'monthly' },
      { description: 'Public Transit', amount: 150, category: 'transportation', frequency: 'monthly' },
      { description: 'Child Care', amount: 1500, category: 'childcare', frequency: 'monthly' },
      { description: 'Children Activities', amount: 400, category: 'childcare', frequency: 'monthly' },
      { description: 'Health Insurance', amount: 200, category: 'health', frequency: 'monthly' },
      { description: 'Medications', amount: 100, category: 'health', frequency: 'monthly' },
      { description: 'Life Insurance', amount: 150, category: 'insurance', frequency: 'monthly' },
      { description: 'Cell Phone', amount: 100, category: 'personal', frequency: 'monthly' },
      { description: 'Clothing', amount: 200, category: 'personal', frequency: 'monthly' },
      { description: 'Entertainment', amount: 200, category: 'personal', frequency: 'monthly' }
    ],
    assets: [
      { 
        description: 'Family Home', 
        currentValue: 850000, 
        dateAcquired: '2015-06-15',
        encumbrance: 450000
      },
      { 
        description: '2021 Honda CR-V', 
        currentValue: 35000,
        dateAcquired: '2021-03-01',
        encumbrance: 20000
      },
      { 
        description: 'TD Chequing Account', 
        currentValue: 5000,
        accountNumber: '***4567'
      },
      { 
        description: 'TD Savings Account', 
        currentValue: 25000,
        accountNumber: '***8901'
      },
      { 
        description: 'RRSP - TD Investment', 
        currentValue: 75000,
        accountNumber: '***2345'
      },
      { 
        description: 'TFSA - TD Investment', 
        currentValue: 40000,
        accountNumber: '***6789'
      },
      { 
        description: 'RESP for Children', 
        currentValue: 30000,
        accountNumber: '***3456'
      },
      { 
        description: 'Jewelry', 
        currentValue: 5000,
        description_detail: 'Wedding ring, watch'
      },
      { 
        description: 'Household Items & Furniture', 
        currentValue: 15000
      }
    ],
    debts: [
      { 
        description: 'Mortgage - TD Bank', 
        amount: 450000, 
        creditor: 'TD Canada Trust',
        monthlyPayment: 3200,
        securedBy: 'Family Home'
      },
      { 
        description: 'Car Loan - Honda Finance', 
        amount: 20000, 
        creditor: 'Honda Financial Services',
        monthlyPayment: 650,
        securedBy: '2021 Honda CR-V'
      },
      { 
        description: 'Line of Credit - TD', 
        amount: 15000, 
        creditor: 'TD Canada Trust',
        monthlyPayment: 300
      },
      { 
        description: 'Credit Card - TD Visa', 
        amount: 5000, 
        creditor: 'TD Visa',
        monthlyPayment: 150
      },
      { 
        description: 'Credit Card - Mastercard', 
        amount: 3000, 
        creditor: 'Capital One',
        monthlyPayment: 100
      }
    ],
    taxDocuments: [
      {
        year: 2023,
        t1ReturnPath: './test-files/2023-t1-return.pdf',
        noaPath: './test-files/2023-noa.pdf',
        totalIncome: 114000,
        taxableIncome: 95000,
        taxPaid: 28000
      },
      {
        year: 2022,
        t1ReturnPath: './test-files/2022-t1-return.pdf',
        noaPath: './test-files/2022-noa.pdf',
        totalIncome: 108000,
        taxableIncome: 90000,
        taxPaid: 26000
      },
      {
        year: 2021,
        t1ReturnPath: './test-files/2021-t1-return.pdf',
        noaPath: './test-files/2021-noa.pdf',
        totalIncome: 105000,
        taxableIncome: 87000,
        taxPaid: 25000
      }
    ],
    bankStatements: [
      {
        accountName: 'TD Chequing - ***4567',
        balance: 5000,
        statementPaths: [
          './test-files/td-chequing-2024-01.pdf',
          './test-files/td-chequing-2024-02.pdf',
          './test-files/td-chequing-2024-03.pdf'
        ]
      },
      {
        accountName: 'TD Savings - ***8901',
        balance: 25000,
        statementPaths: [
          './test-files/td-savings-2024-01.pdf',
          './test-files/td-savings-2024-02.pdf',
          './test-files/td-savings-2024-03.pdf'
        ]
      }
    ],
    signature: {
      name: 'Jane Elizabeth Doe',
      date: new Date().toISOString().split('T')[0],
      location: 'Toronto, Ontario'
    }
  },

  // High net worth individual scenario
  highNetWorth: {
    personal: {
      fullName: 'Robert James Wellington III',
      courtName: 'Superior Court of Justice',
      courtFileNumber: 'FC-24-HNW-001',
      lawyerName: 'Margaret Sterling, K.C.',
      lsoNumber: '98765X',
      lawFirm: 'Sterling & Associates LLP'
    },
    contact: {
      address: '1 King Street West, Penthouse, Toronto, ON',
      postalCode: 'M5H 1A1',
      email: 'rwellington@wellington-enterprises.com',
      phone: '416-555-9000',
      mobile: '647-555-9001'
    },
    income: [
      { description: 'Executive Salary - CEO', amount: 50000, frequency: 'monthly', employer: 'Wellington Enterprises Inc.' },
      { description: 'Director Fees', amount: 10000, frequency: 'monthly', source: 'Various Boards' },
      { description: 'Investment Income - Dividends', amount: 25000, frequency: 'monthly', source: 'Investment Portfolio' },
      { description: 'Rental Income - Properties', amount: 15000, frequency: 'monthly', source: '5 Rental Properties' },
      { description: 'Trust Distributions', amount: 20000, frequency: 'quarterly', source: 'Wellington Family Trust' },
      { description: 'Capital Gains', amount: 100000, frequency: 'yearly', source: 'Stock Sales' }
    ],
    expenses: [
      { description: 'Mortgage - Primary Residence', amount: 15000, category: 'housing' },
      { description: 'Mortgage - Muskoka Cottage', amount: 5000, category: 'housing' },
      { description: 'Mortgage - Florida Condo', amount: 8000, category: 'housing' },
      { description: 'Property Tax - All Properties', amount: 5000, category: 'housing' },
      { description: 'Property Management', amount: 2000, category: 'housing' },
      { description: 'Private Chef & Groceries', amount: 5000, category: 'food' },
      { description: 'Fine Dining', amount: 3000, category: 'food' },
      { description: 'Luxury Car Leases (3)', amount: 5000, category: 'transportation' },
      { description: 'Yacht Maintenance', amount: 3000, category: 'transportation' },
      { description: 'Private Jet Fractional', amount: 10000, category: 'transportation' },
      { description: 'Private School (3 children)', amount: 8000, category: 'education' },
      { description: 'University Tuition', amount: 5000, category: 'education' },
      { description: 'Nanny & Household Staff', amount: 10000, category: 'childcare' },
      { description: 'Country Club Memberships', amount: 2000, category: 'recreation' },
      { description: 'Travel & Vacations', amount: 5000, category: 'recreation' },
      { description: 'Art & Collectibles', amount: 5000, category: 'personal' },
      { description: 'Charitable Donations', amount: 10000, category: 'personal' }
    ],
    assets: [
      { description: 'Primary Residence - Toronto', currentValue: 5000000, dateAcquired: '2010-01-01' },
      { description: 'Muskoka Cottage', currentValue: 2000000, dateAcquired: '2015-06-01' },
      { description: 'Florida Condo', currentValue: 1500000, dateAcquired: '2018-03-01' },
      { description: 'Rental Properties (5)', currentValue: 3500000 },
      { description: 'Wellington Enterprises Inc. (60% shares)', currentValue: 25000000 },
      { description: 'Investment Portfolio - Stocks', currentValue: 10000000 },
      { description: 'Investment Portfolio - Bonds', currentValue: 5000000 },
      { description: 'Private Equity Investments', currentValue: 8000000 },
      { description: 'Art Collection', currentValue: 2000000 },
      { description: 'Classic Car Collection (6 cars)', currentValue: 1500000 },
      { description: 'Yacht - 60ft', currentValue: 2000000 },
      { description: 'Jewelry & Watches', currentValue: 500000 },
      { description: 'Wine Collection', currentValue: 250000 },
      { description: 'Bank Accounts - Various', currentValue: 1000000 },
      { description: 'Cryptocurrency Holdings', currentValue: 500000 }
    ],
    debts: [
      { description: 'Mortgage - Primary Residence', amount: 2000000, creditor: 'Private Bank' },
      { description: 'Mortgage - Muskoka', amount: 800000, creditor: 'Private Bank' },
      { description: 'Mortgage - Florida', amount: 600000, creditor: 'US Bank' },
      { description: 'Investment Line of Credit', amount: 5000000, creditor: 'Scotia Wealth' },
      { description: 'Margin Loan', amount: 2000000, creditor: 'TD Wealth' }
    ],
    signature: {
      name: 'Robert James Wellington III',
      date: new Date().toISOString().split('T')[0],
      location: 'Toronto, Ontario'
    }
  },

  // Self-employed/Business owner scenario
  businessOwner: {
    personal: {
      fullName: 'Maria Gonzalez',
      courtName: 'Superior Court of Justice',
      courtFileNumber: 'FC-24-BUS-789'
    },
    contact: {
      address: '789 Entrepreneur Way, Mississauga, ON',
      postalCode: 'L5B 4G5',
      email: 'maria@gonzalez-consulting.com',
      phone: '905-555-0300',
      businessPhone: '905-555-0301'
    },
    income: [
      { description: 'Business Income - Consulting', amount: 15000, frequency: 'monthly', source: 'Gonzalez Consulting Inc.' },
      { description: 'Dividend Income', amount: 5000, frequency: 'quarterly', source: 'Gonzalez Consulting Inc.' },
      { description: 'Contract Work', amount: 3000, frequency: 'monthly', source: 'Various Clients' }
    ],
    expenses: [
      { description: 'Mortgage', amount: 2500, category: 'housing' },
      { description: 'Business Rent', amount: 2000, category: 'business' },
      { description: 'Business Insurance', amount: 500, category: 'business' },
      { description: 'Business Marketing', amount: 1000, category: 'business' },
      { description: 'Professional Development', amount: 500, category: 'business' },
      { description: 'Accounting & Legal', amount: 1000, category: 'business' },
      { description: 'Personal Expenses', amount: 3000, category: 'personal' }
    ],
    assets: [
      { description: 'Business (100% ownership)', currentValue: 500000 },
      { description: 'Business Equipment', currentValue: 50000 },
      { description: 'Accounts Receivable', currentValue: 75000 },
      { description: 'Home', currentValue: 650000 },
      { description: 'Business Vehicle', currentValue: 45000 },
      { description: 'Business Bank Account', currentValue: 50000 },
      { description: 'Personal Savings', currentValue: 30000 }
    ],
    debts: [
      { description: 'Business Loan', amount: 150000, creditor: 'BDC' },
      { description: 'Business Line of Credit', amount: 50000, creditor: 'RBC Business' },
      { description: 'Business Credit Card', amount: 10000, creditor: 'American Express Business' },
      { description: 'Home Mortgage', amount: 400000, creditor: 'Scotia Bank' }
    ],
    signature: {
      name: 'Maria Gonzalez',
      date: new Date().toISOString().split('T')[0],
      location: 'Mississauga, Ontario'
    }
  },

  // Support recipient with limited income
  supportRecipient: {
    personal: {
      fullName: 'Sarah Johnson',
      courtName: 'Ontario Court of Justice',
      courtFileNumber: 'FS-24-456'
    },
    contact: {
      address: '50 Struggle Street, Hamilton, ON',
      postalCode: 'L8N 3T1',
      email: 'sjohnson@email.com',
      phone: '905-555-0400'
    },
    income: [
      { description: 'Part-time Employment', amount: 1800, frequency: 'monthly', employer: 'Retail Store' },
      { description: 'Child Support', amount: 1500, frequency: 'monthly', source: 'Ex-spouse' },
      { description: 'Child Tax Benefit', amount: 650, frequency: 'monthly', source: 'CRA' },
      { description: 'Ontario Works', amount: 733, frequency: 'monthly', source: 'Ontario Government' }
    ],
    expenses: [
      { description: 'Rent', amount: 1500, category: 'housing' },
      { description: 'Utilities', amount: 200, category: 'housing' },
      { description: 'Groceries', amount: 800, category: 'food' },
      { description: 'Children Clothing', amount: 200, category: 'childcare' },
      { description: 'School Supplies', amount: 100, category: 'childcare' },
      { description: 'Public Transit', amount: 150, category: 'transportation' },
      { description: 'Cell Phone', amount: 50, category: 'personal' },
      { description: 'Medications', amount: 100, category: 'health' },
      { description: 'Debt Payments', amount: 200, category: 'debt' }
    ],
    assets: [
      { description: '2010 Honda Civic', currentValue: 5000 },
      { description: 'Bank Account', currentValue: 500 },
      { description: 'Household Items', currentValue: 3000 }
    ],
    debts: [
      { description: 'Credit Card', amount: 8000, creditor: 'Capital One' },
      { description: 'Payday Loan', amount: 2000, creditor: 'Money Mart' },
      { description: 'Utility Arrears', amount: 1500, creditor: 'Hydro One' }
    ],
    signature: {
      name: 'Sarah Johnson',
      date: new Date().toISOString().split('T')[0],
      location: 'Hamilton, Ontario'
    }
  },

  // Edge case: Unemployed with no income
  unemployed: {
    personal: {
      fullName: 'David Miller',
      courtName: 'Ontario Court of Justice',
      courtFileNumber: 'FS-24-789'
    },
    contact: {
      address: '123 Hardship Ave, Windsor, ON',
      postalCode: 'N9A 1A1',
      email: 'dmiller@email.com',
      phone: '519-555-0500'
    },
    income: [
      { description: 'Employment Insurance', amount: 2000, frequency: 'monthly', source: 'Service Canada' },
      { description: 'Occasional Gig Work', amount: 200, frequency: 'monthly', source: 'Various' }
    ],
    expenses: [
      { description: 'Room Rental', amount: 600, category: 'housing' },
      { description: 'Food', amount: 400, category: 'food' },
      { description: 'Phone', amount: 40, category: 'personal' },
      { description: 'Transportation', amount: 100, category: 'transportation' }
    ],
    assets: [
      { description: 'Personal Items', currentValue: 1000 }
    ],
    debts: [
      { description: 'Student Loan', amount: 25000, creditor: 'OSAP' },
      { description: 'Credit Card', amount: 5000, creditor: 'TD Visa' }
    ],
    signature: {
      name: 'David Miller',
      date: new Date().toISOString().split('T')[0],
      location: 'Windsor, Ontario'
    }
  }
};

// Validation test data with invalid inputs
const invalidTestData = {
  invalidEmails: [
    'notanemail',
    '@example.com',
    'user@',
    'user@.com',
    'user@domain',
    'user name@example.com',
    'user@domain..com'
  ],
  
  invalidPhoneNumbers: [
    '123',
    'abcdefghij',
    '555-CALL-ME',
    '1234567890123456', // Too long
    '(416) 555-01234'   // Extra digit
  ],
  
  invalidPostalCodes: [
    '12345',      // US ZIP
    '123456',     // Invalid length
    'ABCDEF',     // No numbers
    'Z9Z 9Z9',    // Z not used in first position
    'D9D 9D9',    // D not used
    'F9F 9F9',    // F not used
    'I9I 9I9',    // I not used
    'O9O 9O9',    // O not used
    'Q9Q 9Q9',    // Q not used
    'U9U 9U9',    // U not used
    'K1A0B1',     // Missing space
    'K1A  0B1',   // Too many spaces
    'K1A-0B1'     // Wrong separator
  ],
  
  validOntarioPostalCodes: [
    'K1A 0B1',  // Ottawa
    'M5H 2N2',  // Toronto
    'M4V 1L9',  // Toronto
    'N6A 5B6',  // London
    'L5B 4G5',  // Mississauga
    'L6H 7V2',  // Oakville
    'P0A 1A0',  // Northern Ontario
    'K7K 7L1',  // Kingston
    'N2L 3G1',  // Waterloo
    'L8S 4L8'   // Hamilton
  ],
  
  invalidCurrencyAmounts: [
    'abc',
    '12.34.56',
    '$12,34',
    '12e5',
    '-1000',    // Negative
    '1.234',    // Too many decimals
    '€100',     // Wrong currency symbol
    '100 CAD'   // Text suffix
  ],
  
  invalidDates: [
    '2030-01-01',  // Future date (for DOB)
    '1800-01-01',  // Too old
    '02-30-2024',  // Invalid date
    '13-01-2024',  // Invalid month
    'yesterday',   // Text
    '2024/01/01'   // Wrong format
  ],
  
  specialCharacterInputs: [
    "O'Brien",
    "Anne-Marie",
    "José García",
    "Müller",
    "Владимир",
    "李明",
    "Smith, Jr.",
    "ABC & Co.",
    "Test (Special) #123",
    "50% ownership",
    "$pecial Char@cters!"
  ],
  
  maxLengthInputs: {
    veryLongName: 'A'.repeat(256),
    veryLongDescription: 'This is a test description. '.repeat(100),
    veryLongAddress: '123 This Is An Extremely Long Street Name That Should Be Truncated, Apartment 9999, Building Complex Name Here, Toronto, Ontario, Canada',
    maxCurrency: '99999999999.99',
    minCurrency: '0.01'
  }
};

// Helper function to generate random test data
function generateRandomTestData() {
  const firstNames = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa'];
  const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'];
  const streets = ['Main', 'Queen', 'King', 'Bay', 'Yonge', 'Bloor', 'College', 'Dundas'];
  const cities = ['Toronto', 'Ottawa', 'Mississauga', 'Hamilton', 'London', 'Waterloo', 'Kingston', 'Windsor'];
  
  const randomFirstName = firstNames[Math.floor(Math.random() * firstNames.length)];
  const randomLastName = lastNames[Math.floor(Math.random() * lastNames.length)];
  const randomStreet = streets[Math.floor(Math.random() * streets.length)];
  const randomCity = cities[Math.floor(Math.random() * cities.length)];
  
  return {
    personal: {
      fullName: `${randomFirstName} ${randomLastName}`,
      courtName: 'Superior Court of Justice',
      courtFileNumber: `FC-24-${Math.floor(Math.random() * 9999).toString().padStart(4, '0')}`
    },
    contact: {
      address: `${Math.floor(Math.random() * 999) + 1} ${randomStreet} Street, ${randomCity}, ON`,
      postalCode: `M${Math.floor(Math.random() * 9) + 1}H ${Math.floor(Math.random() * 9) + 1}N${Math.floor(Math.random() * 9) + 1}`,
      email: `${randomFirstName.toLowerCase()}.${randomLastName.toLowerCase()}@example.com`,
      phone: `416-555-${Math.floor(Math.random() * 9000 + 1000)}`
    },
    income: [
      { 
        description: 'Employment Income', 
        amount: Math.floor(Math.random() * 10000 + 2000), 
        frequency: 'monthly'
      }
    ],
    expenses: [
      { 
        description: 'Housing', 
        amount: Math.floor(Math.random() * 3000 + 1000), 
        category: 'housing'
      },
      { 
        description: 'Food', 
        amount: Math.floor(Math.random() * 1000 + 300), 
        category: 'food'
      }
    ],
    assets: [
      { 
        description: 'Savings', 
        currentValue: Math.floor(Math.random() * 50000 + 1000)
      }
    ],
    debts: [
      { 
        description: 'Credit Card', 
        amount: Math.floor(Math.random() * 10000 + 500),
        creditor: 'Bank'
      }
    ],
    signature: {
      name: `${randomFirstName} ${randomLastName}`,
      date: new Date().toISOString().split('T')[0],
      location: `${randomCity}, Ontario`
    }
  };
}

// Function to get test data by scenario name
function getTestData(scenario) {
  if (scenario === 'random') {
    return generateRandomTestData();
  }
  return testScenarios[scenario] || testScenarios.minimal;
}

// Export for use in tests
module.exports = {
  testScenarios,
  invalidTestData,
  generateRandomTestData,
  getTestData,
  generateTestData: getTestData // Alias for compatibility
};