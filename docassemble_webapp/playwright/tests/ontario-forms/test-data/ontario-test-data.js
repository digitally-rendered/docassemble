// Test data for Ontario Family Law Forms
export const testData = {
  // Common test data for all forms
  common: {
    courtInfo: {
      courtName: "Superior Court of Justice - Family Court",
      courtFileNumber: "FC-2025-001234",
      courtAddress: "393 University Avenue, Toronto, ON M5G 1E6",
      municipality: "Toronto"
    },
    
    // Sample applicant data
    applicant: {
      firstName: "Sarah",
      lastName: "Thompson",
      middleName: "Elizabeth",
      fullLegalName: "Sarah Elizabeth Thompson",
      dateOfBirth: "1985-03-15",
      address: {
        street: "123 Queen Street West",
        city: "Toronto",
        province: "Ontario",
        postalCode: "M5H 2M9",
        country: "Canada"
      },
      phone: "(416) 555-0123",
      email: "sarah.thompson@example.com",
      sin: "123-456-789",
      lawyerInfo: {
        name: "Jennifer Roberts",
        firmName: "Roberts Family Law",
        lsoNumber: "12345R",
        address: "456 Bay Street, Suite 800",
        city: "Toronto",
        postalCode: "M5J 2L8",
        phone: "(416) 555-9876",
        email: "jroberts@robertslaw.ca"
      }
    },
    
    // Sample respondent data
    respondent: {
      firstName: "Michael",
      lastName: "Thompson",
      middleName: "James",
      fullLegalName: "Michael James Thompson",
      dateOfBirth: "1983-07-22",
      address: {
        street: "789 King Street East",
        city: "Hamilton",
        province: "Ontario",
        postalCode: "L8M 1A1",
        country: "Canada"
      },
      phone: "(905) 555-4567",
      email: "michael.thompson@example.com",
      sin: "987-654-321"
    },
    
    // Marriage information
    marriage: {
      dateOfMarriage: "2010-06-15",
      placeOfMarriage: "Toronto, Ontario, Canada",
      dateOfSeparation: "2024-01-15",
      dateOfCohabitation: "2009-01-01",
      adultery: false,
      cruelty: false,
      separationOneYear: true
    },
    
    // Children information
    children: [
      {
        firstName: "Emma",
        lastName: "Thompson",
        dateOfBirth: "2012-09-10",
        placeOfBirth: "Toronto, Ontario",
        residesWith: "applicant",
        school: "Rosedale Public School",
        grade: "Grade 7"
      },
      {
        firstName: "Lucas",
        lastName: "Thompson",
        dateOfBirth: "2015-04-25",
        placeOfBirth: "Toronto, Ontario",
        residesWith: "applicant",
        school: "Rosedale Public School",
        grade: "Grade 4"
      }
    ]
  },
  
  // Form-specific test data
  form8A: {
    groundsForDivorce: "separation",
    claimCustody: true,
    claimSupport: true,
    claimProperty: true,
    claimCosts: false,
    reconciliationAttempts: "Marriage counselling from January 2023 to June 2023",
    barriers: "None",
    previousProceedings: false
  },
  
  form13: {
    employment: {
      employer: "Tech Solutions Inc.",
      position: "Senior Software Developer",
      startDate: "2018-03-01",
      grossMonthlyIncome: 8500.00,
      netMonthlyIncome: 6200.00
    },
    otherIncome: {
      investments: 250.00,
      rentalIncome: 0,
      governmentBenefits: 500.00,
      other: 0
    },
    monthlyExpenses: {
      housing: 2500.00,
      utilities: 250.00,
      food: 800.00,
      clothing: 200.00,
      transportation: 450.00,
      healthCare: 150.00,
      childCare: 1200.00,
      insurance: 350.00,
      debtPayments: 400.00,
      other: 300.00
    },
    assets: {
      realEstate: 650000.00,
      vehicles: 35000.00,
      bankAccounts: 45000.00,
      investments: 125000.00,
      rrsp: 85000.00,
      pension: 150000.00,
      personalProperty: 25000.00
    },
    debts: {
      mortgage: 380000.00,
      creditCards: 5000.00,
      loans: 15000.00,
      other: 0
    }
  },
  
  form10: {
    disputeClaims: {
      custody: true,
      support: false,
      property: true,
      other: false
    },
    counterClaims: {
      jointCustody: true,
      spousalSupport: true,
      equalPropertyDivision: true
    },
    response: "The respondent disputes the applicant's claims regarding sole custody and requests joint custody arrangement."
  },
  
  form36: {
    marriageCertificateAttached: true,
    noReconciliation: true,
    arrangementsForChildren: "Joint custody with primary residence with applicant. Regular access schedule every other weekend and Wednesday evenings.",
    childSupport: {
      payorIncome: 102000.00,
      tableAmount: 1471.00,
      specialExpenses: 400.00,
      totalMonthly: 1871.00
    },
    spousalSupport: {
      amount: 1500.00,
      duration: "5 years or until remarriage",
      indexed: true
    },
    propertySettlement: "Equal division of net family property as per Form 13B calculations"
  },
  
  form25A: {
    divorceGrantedDate: "2025-03-15",
    effectiveDate: "2025-04-16",
    judgeAddress: "The Honourable Justice M. Smith",
    custodyOrder: "Joint custody with primary residence to applicant",
    supportOrder: "Child support of $1,871 per month, spousal support of $1,500 per month",
    propertyOrder: "Equalization payment of $75,000 from respondent to applicant",
    costsOrder: "No order as to costs"
  }
};

// Helper functions for test data
export const getRandomPhoneNumber = () => {
  const areaCode = ['416', '647', '905', '289', '519', '613'][Math.floor(Math.random() * 6)];
  return `(${areaCode}) 555-${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}`;
};

export const getRandomPostalCode = () => {
  const letters = 'KLMNP';
  const firstLetter = letters[Math.floor(Math.random() * letters.length)];
  const digit1 = Math.floor(Math.random() * 10);
  const letter2 = String.fromCharCode(65 + Math.floor(Math.random() * 26));
  const digit2 = Math.floor(Math.random() * 10);
  const letter3 = String.fromCharCode(65 + Math.floor(Math.random() * 26));
  const digit3 = Math.floor(Math.random() * 10);
  return `${firstLetter}${digit1}${letter2} ${digit2}${letter3}${digit3}`;
};

export const getRandomCourtFileNumber = () => {
  const year = new Date().getFullYear();
  const number = Math.floor(Math.random() * 999999).toString().padStart(6, '0');
  return `FC-${year}-${number}`;
};

export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD'
  }).format(amount);
};

export default testData;