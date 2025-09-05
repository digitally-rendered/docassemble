/**
 * Ontario Family Law Forms - Comprehensive Test Data Fixtures
 * 
 * This file contains realistic test data for Ontario residents
 * to be used in automated Playwright tests for all Ontario Family Law forms.
 */

const ontarioTestData = {
  // Sample Ontario residents with diverse backgrounds
  applicants: {
    standard: {
      firstName: 'Jennifer',
      middleName: 'Marie',
      lastName: 'Thompson',
      dateOfBirth: '1985-03-15',
      gender: 'Female',
      email: 'jennifer.thompson@example.com',
      phone: '416-555-0123',
      cellPhone: '647-555-0124',
      address: {
        street: '123 Queen Street West',
        unit: 'Unit 2B',
        city: 'Toronto',
        province: 'Ontario',
        postalCode: 'M5H 2M9',
        country: 'Canada'
      },
      mailingAddress: {
        sameAsResidence: true
      },
      sin: '123-456-789',
      healthCardNumber: '1234-567-890-AB',
      driversLicense: 'T4567-89012-34567'
    },
    secondary: {
      firstName: 'Michael',
      middleName: 'James',
      lastName: 'Anderson',
      dateOfBirth: '1982-07-22',
      gender: 'Male',
      email: 'michael.anderson@example.com',
      phone: '905-555-0234',
      cellPhone: '289-555-0235',
      address: {
        street: '456 Main Street',
        unit: '',
        city: 'Mississauga',
        province: 'Ontario',
        postalCode: 'L5B 4L8',
        country: 'Canada'
      },
      sin: '987-654-321',
      healthCardNumber: '9876-543-210-CD',
      driversLicense: 'A9876-54321-09876'
    },
    minimalInfo: {
      firstName: 'Sarah',
      lastName: 'Wilson',
      dateOfBirth: '1990-11-30',
      email: 'sarah.wilson@example.com',
      phone: '613-555-0345',
      address: {
        street: '789 Bank Street',
        city: 'Ottawa',
        province: 'Ontario',
        postalCode: 'K1S 3T4',
        country: 'Canada'
      }
    }
  },

  respondents: {
    standard: {
      firstName: 'Robert',
      middleName: 'William',
      lastName: 'Thompson',
      dateOfBirth: '1983-09-28',
      gender: 'Male',
      email: 'robert.thompson@example.com',
      phone: '416-555-0456',
      cellPhone: '647-555-0457',
      address: {
        street: '789 King Street East',
        unit: 'Apt 15',
        city: 'Toronto',
        province: 'Ontario',
        postalCode: 'M5A 1K9',
        country: 'Canada'
      },
      sin: '456-789-123',
      healthCardNumber: '4567-890-123-EF',
      driversLicense: 'T1234-56789-01234'
    },
    secondary: {
      firstName: 'Emily',
      middleName: 'Anne',
      lastName: 'Anderson',
      dateOfBirth: '1984-12-05',
      gender: 'Female',
      email: 'emily.anderson@example.com',
      phone: '905-555-0567',
      cellPhone: '289-555-0568',
      address: {
        street: '321 Lakeshore Road',
        city: 'Oakville',
        province: 'Ontario',
        postalCode: 'L6J 1J3',
        country: 'Canada'
      }
    }
  },

  children: [
    {
      firstName: 'Emma',
      middleName: 'Grace',
      lastName: 'Thompson',
      dateOfBirth: '2015-06-12',
      gender: 'Female',
      birthplace: 'Toronto, Ontario',
      residesWithApplicant: true,
      residesWithRespondent: false,
      school: 'Rosedale Public School',
      grade: '4',
      healthCardNumber: '1111-222-333-GH'
    },
    {
      firstName: 'Liam',
      middleName: 'Alexander',
      lastName: 'Thompson',
      dateOfBirth: '2017-09-03',
      gender: 'Male',
      birthplace: 'Toronto, Ontario',
      residesWithApplicant: true,
      residesWithRespondent: false,
      school: 'Rosedale Public School',
      grade: '2',
      healthCardNumber: '2222-333-444-IJ'
    },
    {
      firstName: 'Sophia',
      lastName: 'Thompson',
      dateOfBirth: '2020-02-14',
      gender: 'Female',
      birthplace: 'Mississauga, Ontario',
      residesWithApplicant: false,
      residesWithRespondent: true,
      school: 'Little Learners Daycare',
      healthCardNumber: '3333-444-555-KL'
    }
  ],

  lawyers: {
    applicantLawyer: {
      firstName: 'David',
      lastName: 'Mitchell',
      firmName: 'Mitchell & Associates LLP',
      lsucNumber: '12345A',
      email: 'david.mitchell@mitchelllaw.ca',
      phone: '416-555-0789',
      fax: '416-555-0790',
      address: {
        street: '100 Bay Street',
        suite: 'Suite 2500',
        city: 'Toronto',
        province: 'Ontario',
        postalCode: 'M5J 2N8',
        country: 'Canada'
      }
    },
    respondentLawyer: {
      firstName: 'Susan',
      lastName: 'Clarke',
      firmName: 'Clarke Legal Services',
      lsucNumber: '67890B',
      email: 'susan.clarke@clarkelegal.ca',
      phone: '416-555-0891',
      fax: '416-555-0892',
      address: {
        street: '200 University Avenue',
        suite: 'Suite 1800',
        city: 'Toronto',
        province: 'Ontario',
        postalCode: 'M5H 3C6',
        country: 'Canada'
      }
    }
  },

  courts: {
    toronto: {
      name: 'Superior Court of Justice',
      fileNumber: 'FC-24-12345',
      address: {
        street: '393 University Avenue',
        city: 'Toronto',
        province: 'Ontario',
        postalCode: 'M5G 1E6',
        country: 'Canada'
      },
      branch: 'Family Court Branch'
    },
    ottawa: {
      name: 'Superior Court of Justice',
      fileNumber: 'FC-24-67890',
      address: {
        street: '161 Elgin Street',
        city: 'Ottawa',
        province: 'Ontario',
        postalCode: 'K2P 2K1',
        country: 'Canada'
      },
      branch: 'Family Court Branch'
    },
    brampton: {
      name: 'Superior Court of Justice',
      fileNumber: 'FC-24-34567',
      address: {
        street: '7755 Hurontario Street',
        city: 'Brampton',
        province: 'Ontario',
        postalCode: 'L6W 4T1',
        country: 'Canada'
      },
      branch: 'Family Court Branch'
    }
  },

  financialData: {
    employment: {
      current: {
        employer: 'Tech Solutions Inc.',
        position: 'Senior Software Developer',
        startDate: '2018-01-15',
        annualSalary: 95000,
        monthlyIncome: 7916.67,
        payFrequency: 'bi-weekly',
        hoursPerWeek: 40,
        employerAddress: {
          street: '500 Wellington Street West',
          city: 'Toronto',
          province: 'Ontario',
          postalCode: 'M5V 2T5'
        }
      },
      previous: {
        employer: 'Digital Innovations Ltd.',
        position: 'Software Developer',
        startDate: '2015-06-01',
        endDate: '2017-12-31',
        annualSalary: 75000,
        reason: 'Better opportunity'
      }
    },
    
    income: {
      employmentIncome: 95000,
      selfEmploymentIncome: 0,
      investmentIncome: 3500,
      rentalIncome: 0,
      pensionIncome: 0,
      governmentBenefits: 0,
      childSupportReceived: 0,
      spousalSupportReceived: 0,
      otherIncome: 0,
      totalAnnualIncome: 98500,
      totalMonthlyIncome: 8208.33
    },

    expenses: {
      housing: {
        rentOrMortgage: 2500,
        propertyTax: 450,
        homeInsurance: 150,
        utilities: 250,
        maintenance: 200,
        condoFees: 0
      },
      living: {
        groceries: 800,
        clothing: 200,
        personalCare: 100,
        medical: 150,
        dental: 75,
        prescriptions: 50,
        transportation: 400,
        carPayment: 450,
        carInsurance: 200,
        gasAndMaintenance: 250
      },
      childRelated: {
        childcare: 1500,
        activities: 300,
        schoolSupplies: 100,
        clothing: 150,
        medical: 50,
        other: 100
      },
      debts: {
        creditCards: 300,
        lineOfCredit: 200,
        studentLoans: 0,
        otherLoans: 0
      },
      totalMonthlyExpenses: 8175
    },

    assets: {
      realEstate: [
        {
          type: 'Matrimonial Home',
          address: '123 Queen Street West, Toronto, ON',
          currentValue: 850000,
          mortgage: 425000,
          equity: 425000,
          ownership: 'Joint',
          dateAcquired: '2016-05-15'
        }
      ],
      vehicles: [
        {
          type: 'Car',
          make: 'Honda',
          model: 'CR-V',
          year: 2021,
          value: 35000,
          loan: 15000,
          ownership: 'Applicant'
        },
        {
          type: 'Car',
          make: 'Toyota',
          model: 'Camry',
          year: 2019,
          value: 25000,
          loan: 0,
          ownership: 'Respondent'
        }
      ],
      bankAccounts: [
        {
          type: 'Chequing',
          institution: 'TD Bank',
          accountNumber: '****1234',
          balance: 5500,
          ownership: 'Applicant'
        },
        {
          type: 'Savings',
          institution: 'TD Bank',
          accountNumber: '****5678',
          balance: 25000,
          ownership: 'Joint'
        }
      ],
      investments: [
        {
          type: 'RRSP',
          institution: 'TD Waterhouse',
          value: 75000,
          ownership: 'Applicant'
        },
        {
          type: 'TFSA',
          institution: 'TD Waterhouse',
          value: 45000,
          ownership: 'Applicant'
        }
      ],
      personalProperty: {
        furniture: 15000,
        electronics: 5000,
        jewelry: 3000,
        art: 2000,
        other: 5000
      },
      totalAssets: 1090500
    },

    debts: {
      mortgage: {
        lender: 'TD Bank',
        balance: 425000,
        monthlyPayment: 2100,
        property: '123 Queen Street West'
      },
      carLoans: [
        {
          lender: 'Honda Finance',
          balance: 15000,
          monthlyPayment: 450,
          vehicle: '2021 Honda CR-V'
        }
      ],
      creditCards: [
        {
          issuer: 'TD Visa',
          balance: 3500,
          limit: 10000,
          minimumPayment: 105
        },
        {
          issuer: 'Mastercard',
          balance: 1500,
          limit: 5000,
          minimumPayment: 45
        }
      ],
      lineOfCredit: {
        lender: 'TD Bank',
        balance: 8000,
        limit: 20000,
        monthlyPayment: 200
      },
      totalDebts: 453000
    }
  },

  marriageData: {
    dateOfMarriage: '2012-07-14',
    placeOfMarriage: 'Toronto, Ontario, Canada',
    dateOfSeparation: '2023-09-15',
    dateOfCohabitation: '2010-03-01',
    reasonForBreakdown: 'Separation for at least one year',
    reconciliationAttempted: true,
    reconciliationDates: {
      start: '2023-03-01',
      end: '2023-04-15'
    },
    previousMarriages: {
      applicant: false,
      respondent: false
    }
  },

  // Edge case data for validation testing
  edgeCases: {
    dates: {
      futureDate: '2030-01-01',
      pastCentury: '1923-01-01',
      today: new Date().toISOString().split('T')[0],
      leapYear: '2024-02-29',
      invalidFormat: '31/12/2023',
      emptyDate: '',
      nullDate: null
    },
    
    currency: {
      zero: 0,
      negative: -100,
      decimal: 1234.56,
      largeAmount: 999999999,
      invalidFormat: '$1,234.56',
      stringAmount: 'one thousand',
      emptyAmount: '',
      nullAmount: null
    },

    text: {
      empty: '',
      spaces: '   ',
      specialChars: "O'Brien-Smith & Co.",
      unicode: 'Montréal, Québec',
      veryLong: 'A'.repeat(500),
      htmlTags: '<script>alert("test")</script>',
      sqlInjection: "'; DROP TABLE users; --",
      numbers: '12345',
      mixed: 'John123 Doe456'
    },

    email: {
      valid: 'test@example.com',
      validComplex: 'user+tag@sub.example.co.uk',
      invalid: 'not-an-email',
      missingAt: 'user.example.com',
      missingDomain: 'user@',
      missingLocal: '@example.com',
      multipleAt: 'user@@example.com',
      spaces: 'user @example.com'
    },

    phone: {
      valid10Digit: '4165551234',
      validFormatted: '(416) 555-1234',
      validWithCountry: '+1-416-555-1234',
      invalid: '123',
      letters: 'CALL-NOW',
      tooLong: '41655512345678',
      extension: '416-555-1234 x123'
    },

    postalCode: {
      validUpperCase: 'M5H 2M9',
      validLowerCase: 'm5h 2m9',
      validNoSpace: 'M5H2M9',
      invalidFormat: '12345',
      invalidLetters: 'XXX XXX',
      partial: 'M5H',
      tooLong: 'M5H 2M9X'
    }
  },

  // Conditional logic test scenarios
  conditionalScenarios: {
    custody: {
      soleToApplicant: {
        arrangement: 'sole',
        primaryParent: 'applicant',
        accessSchedule: 'Every other weekend'
      },
      joint: {
        arrangement: 'joint',
        schedule: '50/50',
        decisionMaking: 'joint'
      },
      shared: {
        arrangement: 'shared',
        percentageWithApplicant: 60,
        percentageWithRespondent: 40
      }
    },

    support: {
      childSupport: {
        payorIncome: 85000,
        recipientIncome: 45000,
        numberOfChildren: 2,
        specialExpenses: true,
        extraordinaryExpenses: ['Private school', 'Medical treatments']
      },
      spousalSupport: {
        lengthOfMarriage: 11,
        payorIncome: 95000,
        recipientIncome: 35000,
        needsBased: true,
        compensatory: true
      }
    },

    property: {
      equalDivision: true,
      exclusions: ['Inheritance', 'Pre-marital assets'],
      matrimonialHome: {
        keepHome: 'applicant',
        buyout: true,
        buyoutAmount: 212500
      }
    }
  }
};

// Helper functions for generating test data
const testDataHelpers = {
  /**
   * Generate a random Ontario postal code
   */
  generatePostalCode: () => {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    return `${letters[Math.floor(Math.random() * 26)]}${numbers[Math.floor(Math.random() * 10)]}${letters[Math.floor(Math.random() * 26)]} ${numbers[Math.floor(Math.random() * 10)]}${letters[Math.floor(Math.random() * 26)]}${numbers[Math.floor(Math.random() * 10)]}`;
  },

  /**
   * Generate a random Ontario phone number
   */
  generatePhoneNumber: (areaCode = '416') => {
    const exchange = Math.floor(Math.random() * 900) + 100;
    const number = Math.floor(Math.random() * 9000) + 1000;
    return `${areaCode}-${exchange}-${number}`;
  },

  /**
   * Generate a random date within a range
   */
  generateRandomDate: (startYear = 1970, endYear = 2023) => {
    const start = new Date(startYear, 0, 1);
    const end = new Date(endYear, 11, 31);
    const randomDate = new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
    return randomDate.toISOString().split('T')[0];
  },

  /**
   * Generate a random dollar amount
   */
  generateRandomAmount: (min = 0, max = 100000) => {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  },

  /**
   * Get test data for a specific form
   */
  getFormSpecificData: (formNumber) => {
    const baseData = {
      applicant: ontarioTestData.applicants.standard,
      respondent: ontarioTestData.respondents.standard,
      court: ontarioTestData.courts.toronto,
      children: ontarioTestData.children
    };

    // Add form-specific data based on form number
    switch(formNumber) {
      case '8A': // Application Divorce
        return {
          ...baseData,
          marriage: ontarioTestData.marriageData,
          grounds: 'Separation for at least one year',
          claimDivorce: true,
          claimCustody: true,
          claimSupport: true,
          claimProperty: true
        };
      
      case '13': // Financial Statement Support
        return {
          ...baseData,
          financial: ontarioTestData.financialData,
          supportClaim: true,
          childSupport: true,
          spousalSupport: true
        };
      
      case '10': // Answer
        return {
          ...baseData,
          dispute: ['custody', 'support amount'],
          agreeWith: ['divorce', 'property division'],
          counterClaim: true
        };
      
      case '36': // Affidavit for Divorce
        return {
          ...baseData,
          marriage: ontarioTestData.marriageData,
          affidavitStatements: {
            separation: true,
            noReconciliation: true,
            childArrangements: true,
            noCollusion: true
          }
        };
      
      case '25A': // Divorce Order
        return {
          ...baseData,
          orderDate: new Date().toISOString().split('T')[0],
          judge: 'The Honourable Justice Smith',
          divorceEffectiveDate: new Date(Date.now() + 31 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
        };
      
      default:
        return baseData;
    }
  }
};

module.exports = {
  ontarioTestData,
  testDataHelpers
};