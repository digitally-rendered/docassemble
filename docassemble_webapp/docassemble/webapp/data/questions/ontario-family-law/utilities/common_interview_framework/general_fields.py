"""
General purpose fields used across multiple forms
Generated module for general_fields fields.
"""
from docassemble.base.util import DADict, DAObject
from .base_objects import *
from .validation_functions import *

class GeneralFieldsModule(DAObject):
    """
    General purpose fields used across multiple forms
    
    Dependencies: court_case_info
    """
    
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # Initialize field attributes
        self.total = ""
        self.1 = ""
        self.total_of_property = ""
        self.total_3_from = ""
        self.total_5_total = ""
        self.total_6_net = ""
        self.including_travel_including = ""
        self.a_totals_value = ""
        self.b_totals_value = ""
        self.c_totals_value = ""
        self.d_totals_cash = ""
        self.e_totals_value = ""
        self.g_totals_value = ""
        self.totals_value_of = ""
        self.4_employment_insurance = ""
        self.ei_premiums_ei = ""
        self.subtotal_car_loan = ""
        self.housing_subtotal = ""
        self.rent_or_mortgage = ""
        self.property_taxes_property = ""
        self.property_insurance_property = ""
        self.repairs_and_maintenance = ""
        self.water_clothing = ""
        self.heat_hair_care = ""
        self.electricity_alcohol_and = ""
        self.cable_gifts = ""
        self.internet_subtotal_subtot = ""
        self.subtotal_other_expenses = ""
        self.household_expenses_household = ""
        self.meals_outside_the = ""
        self.laundry_and_dry = ""
        self.subtotal_summer_camp = ""
        self.babysitting_costs_babysitting = ""
        self.6_my_spouse = ""
        self.cars_boats_vehicles = ""
        self.4_total_capital = ""
        self.5_registered_retirement = ""
        self.2 = ""
        self.3 = ""
        self.4 = ""
        self.5 = ""
        self.6 = ""
        self.7 = ""
        self.8 = ""
        self.9 = ""
        self.10 = ""
        self.total_net_annual = ""

    def validate_all_fields(self):
        """Validate all fields in this module"""
        errors = []
        return len(errors) == 0, errors

    def generate_yaml_questions(self, prefix=""):
        """Generate YAML question blocks for this module"""
        questions = []

        # total question
        questions.append({
            "question": "TOTAL TOTAL TOTAL TOTAL TOTAL TOTAL TOTAL TOTAL TO...",
            "fields": [
                {
                    "field": "{prefix}total",
                    "datatype": "text"
                }
            ]
        })

        # 1 question
        questions.append({
            "question": "1. $ $",
            "fields": [
                {
                    "field": "{prefix}1",
                    "datatype": "text"
                }
            ]
        })

        # total_of_property question
        questions.append({
            "question": "TOTAL OF PROPERTY ITEMS TOTAL OF PROPERTY ITEMS $ ...",
            "fields": [
                {
                    "field": "{prefix}total_of_property",
                    "datatype": "text"
                }
            ]
        })

        # total_3_from question
        questions.append({
            "question": "TOTAL 3 (from page 2) $ $ $",
            "fields": [
                {
                    "field": "{prefix}total_3_from",
                    "datatype": "text"
                }
            ]
        })

        # total_5_total question
        questions.append({
            "question": "TOTAL 5 ([Total 2] + [Total 3] +[Total 4]) $ $ $",
            "fields": [
                {
                    "field": "{prefix}total_5_total",
                    "datatype": "text"
                }
            ]
        })

        # total_6_net question
        questions.append({
            "question": "TOTAL 6  NET FAMILY PROPERTY ([Total 1] minus [To...",
            "fields": [
                {
                    "field": "{prefix}total_6_net",
                    "datatype": "text"
                }
            ]
        })

        # including_travel_including question
        questions.append({
            "question": "$ including travel. including travel. including tr...",
            "fields": [
                {
                    "field": "{prefix}including_travel_including",
                    "datatype": "text"
                }
            ]
        })

        # a_totals_value question
        questions.append({
            "question": "(A) TOTALS Value of Land (A) TOTALS Value of Lan...",
            "fields": [
                {
                    "field": "{prefix}a_totals_value",
                    "datatype": "text"
                }
            ]
        })

        # b_totals_value question
        questions.append({
            "question": "(B) TOTALS Value of General Household Items and V...",
            "fields": [
                {
                    "field": "{prefix}b_totals_value",
                    "datatype": "text"
                }
            ]
        })

        # c_totals_value question
        questions.append({
            "question": "(C) TOTALS Value of Accounts and Savings (C) TOTA...",
            "fields": [
                {
                    "field": "{prefix}c_totals_value",
                    "datatype": "text"
                }
            ]
        })

        # d_totals_cash question
        questions.append({
            "question": "(D) TOTALS Cash Surrender Value of Insurance Poli...",
            "fields": [
                {
                    "field": "{prefix}d_totals_cash",
                    "datatype": "text"
                }
            ]
        })

        # e_totals_value question
        questions.append({
            "question": "(E) TOTALS Value of Business Interests (E) TOTALS...",
            "fields": [
                {
                    "field": "{prefix}e_totals_value",
                    "datatype": "text"
                }
            ]
        })

        # g_totals_value question
        questions.append({
            "question": "(G) TOTALS Value of Other Property (G) TOTALS Va...",
            "fields": [
                {
                    "field": "{prefix}g_totals_value",
                    "datatype": "text"
                }
            ]
        })

        # totals_value_of question
        questions.append({
            "question": "TOTALS Value of Debts and Other Liabilities, (TOT...",
            "fields": [
                {
                    "field": "{prefix}totals_value_of",
                    "datatype": "text"
                }
            ]
        })

        # 4_employment_insurance question
        questions.append({
            "question": "4. 4. Employment Insurance benefits Employment Ins...",
            "fields": [
                {
                    "field": "{prefix}4_employment_insurance",
                    "datatype": "text"
                }
            ]
        })

        # ei_premiums_ei question
        questions.append({
            "question": "EI premiums EI premiums EI premiums $ Gas and oil ...",
            "fields": [
                {
                    "field": "{prefix}ei_premiums_ei",
                    "datatype": "text"
                }
            ]
        })

        # subtotal_car_loan question
        questions.append({
            "question": "SUBTOTAL SUBTOTAL SUBTOTAL $ Car Loan or Lease Pay...",
            "fields": [
                {
                    "field": "{prefix}subtotal_car_loan",
                    "datatype": "text"
                }
            ]
        })

        # housing_subtotal question
        questions.append({
            "question": "Housing Housing Housing Housing Housing SUBTOTAL S...",
            "fields": [
                {
                    "field": "{prefix}housing_subtotal",
                    "datatype": "text"
                }
            ]
        })

        # rent_or_mortgage question
        questions.append({
            "question": "Rent or mortgage Rent or mortgage Rent or mortgage...",
            "fields": [
                {
                    "field": "{prefix}rent_or_mortgage",
                    "datatype": "text"
                }
            ]
        })

        # property_taxes_property question
        questions.append({
            "question": "Property taxes Property taxes Property taxes $ Hea...",
            "fields": [
                {
                    "field": "{prefix}property_taxes_property",
                    "datatype": "text"
                }
            ]
        })

        # property_insurance_property question
        questions.append({
            "question": "Property insurance Property insurance Property ins...",
            "fields": [
                {
                    "field": "{prefix}property_insurance_property",
                    "datatype": "text"
                }
            ]
        })

        # repairs_and_maintenance question
        questions.append({
            "question": "Repairs and maintenance Repairs and maintenance Re...",
            "fields": [
                {
                    "field": "{prefix}repairs_and_maintenance",
                    "datatype": "text"
                }
            ]
        })

        # water_clothing question
        questions.append({
            "question": "Water Water Water $ Clothing Clothing Clothing Clo...",
            "fields": [
                {
                    "field": "{prefix}water_clothing",
                    "datatype": "text"
                }
            ]
        })

        # heat_hair_care question
        questions.append({
            "question": "Heat Heat Heat $ Hair care and beauty Hair care an...",
            "fields": [
                {
                    "field": "{prefix}heat_hair_care",
                    "datatype": "text"
                }
            ]
        })

        # electricity_alcohol_and question
        questions.append({
            "question": "Electricity Electricity Electricity $ Alcohol and ...",
            "fields": [
                {
                    "field": "{prefix}electricity_alcohol_and",
                    "datatype": "text"
                }
            ]
        })

        # cable_gifts question
        questions.append({
            "question": "Cable Cable Cable Cable Cable Cable Cable $ $ Gift...",
            "fields": [
                {
                    "field": "{prefix}cable_gifts",
                    "datatype": "text"
                }
            ]
        })

        # internet_subtotal_subtot question
        questions.append({
            "question": "Internet Internet Internet Internet Internet Inter...",
            "fields": [
                {
                    "field": "{prefix}internet_subtotal_subtot",
                    "datatype": "text"
                }
            ]
        })

        # subtotal_other_expenses question
        questions.append({
            "question": "SUBTOTAL SUBTOTAL SUBTOTAL SUBTOTAL SUBTOTAL SUBTO...",
            "fields": [
                {
                    "field": "{prefix}subtotal_other_expenses",
                    "datatype": "text"
                }
            ]
        })

        # household_expenses_household question
        questions.append({
            "question": "Household Expenses Household Expenses Household Ex...",
            "fields": [
                {
                    "field": "{prefix}household_expenses_household",
                    "datatype": "text"
                }
            ]
        })

        # meals_outside_the question
        questions.append({
            "question": "Meals outside the home Meals outside the home Meal...",
            "fields": [
                {
                    "field": "{prefix}meals_outside_the",
                    "datatype": "text"
                }
            ]
        })

        # laundry_and_dry question
        questions.append({
            "question": "Laundry and Dry Cleaning Laundry and Dry Cleaning ...",
            "fields": [
                {
                    "field": "{prefix}laundry_and_dry",
                    "datatype": "text"
                }
            ]
        })

        # subtotal_summer_camp question
        questions.append({
            "question": "SUBTOTAL SUBTOTAL SUBTOTAL SUBTOTAL SUBTOTAL SUBTO...",
            "fields": [
                {
                    "field": "{prefix}subtotal_summer_camp",
                    "datatype": "text"
                }
            ]
        })

        # babysitting_costs_babysitting question
        questions.append({
            "question": "Babysitting costs Babysitting costs Babysitting co...",
            "fields": [
                {
                    "field": "{prefix}babysitting_costs_babysitting",
                    "datatype": "text"
                }
            ]
        })

        # 6_my_spouse question
        questions.append({
            "question": "6. My spouse/partner My spouse/partner My spouse/p...",
            "fields": [
                {
                    "field": "{prefix}6_my_spouse",
                    "datatype": "text"
                }
            ]
        })

        # cars_boats_vehicles question
        questions.append({
            "question": "Cars, boats, vehicles Cars, boats, vehicles $ $ $ ...",
            "fields": [
                {
                    "field": "{prefix}cars_boats_vehicles",
                    "datatype": "text"
                }
            ]
        })

        # 4_total_capital question
        questions.append({
            "question": "4. 4. 4. 4. 4. Total capital gains ($      ) less ...",
            "fields": [
                {
                    "field": "{prefix}4_total_capital",
                    "datatype": "text"
                }
            ]
        })

        # 5_registered_retirement question
        questions.append({
            "question": "5. 5. 5. 5. 5. Registered retirement savings plan ...",
            "fields": [
                {
                    "field": "{prefix}5_registered_retirement",
                    "datatype": "text"
                }
            ]
        })

        # 2 question
        questions.append({
            "question": "2. $ $",
            "fields": [
                {
                    "field": "{prefix}2",
                    "datatype": "text"
                }
            ]
        })

        # 3 question
        questions.append({
            "question": "3. $ $",
            "fields": [
                {
                    "field": "{prefix}3",
                    "datatype": "text"
                }
            ]
        })

        # 4 question
        questions.append({
            "question": "4. $ $",
            "fields": [
                {
                    "field": "{prefix}4",
                    "datatype": "text"
                }
            ]
        })

        # 5 question
        questions.append({
            "question": "5. $ $",
            "fields": [
                {
                    "field": "{prefix}5",
                    "datatype": "text"
                }
            ]
        })

        # 6 question
        questions.append({
            "question": "6. $ $",
            "fields": [
                {
                    "field": "{prefix}6",
                    "datatype": "text"
                }
            ]
        })

        # 7 question
        questions.append({
            "question": "7. $ $",
            "fields": [
                {
                    "field": "{prefix}7",
                    "datatype": "text"
                }
            ]
        })

        # 8 question
        questions.append({
            "question": "8. $ $",
            "fields": [
                {
                    "field": "{prefix}8",
                    "datatype": "text"
                }
            ]
        })

        # 9 question
        questions.append({
            "question": "9. $ $",
            "fields": [
                {
                    "field": "{prefix}9",
                    "datatype": "text"
                }
            ]
        })

        # 10 question
        questions.append({
            "question": "10. 10. $ $",
            "fields": [
                {
                    "field": "{prefix}10",
                    "datatype": "text"
                }
            ]
        })

        # total_net_annual question
        questions.append({
            "question": "Total Net Annual Amount Total Net Annual Amount To...",
            "fields": [
                {
                    "field": "{prefix}total_net_annual",
                    "datatype": "text"
                }
            ]
        })

        return questions
