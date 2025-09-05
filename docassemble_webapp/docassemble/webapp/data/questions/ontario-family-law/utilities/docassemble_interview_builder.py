#!/usr/bin/env python3
"""
Structured Docassemble Interview Builder
Provides clean Python APIs for building Docassemble interview components
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import yaml
from datetime import datetime
import re


class DataType(Enum):
    """Docassemble data types"""
    TEXT = "text"
    NUMBER = "number"
    CURRENCY = "currency"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    EMAIL = "email"
    INTEGER = "integer"
    YESNO = "yesno"
    YESNORADIO = "yesnoradio"
    NOYES = "noyes"
    NOYESRADIO = "noyesradio"
    FILE = "file"
    FILES = "files"
    CAMERA = "camera"
    USER = "user"
    ENVIRONMENT = "environment"
    BOOLEAN = "boolean"
    CHECKBOXES = "checkboxes"
    RADIO = "radio"
    COMBOBOX = "combobox"
    AJAX = "ajax"
    ML = "ml"
    MLAREA = "mlarea"
    AREA = "area"
    HTML = "html"
    RAW = "raw"


class ProgressBarMethod(Enum):
    """Progress bar display methods"""
    DEFAULT = "default"
    STEPPED = "stepped"
    PERCENTAGE = "percentage"


@dataclass
class Metadata:
    """Interview metadata"""
    title: str
    short_title: Optional[str] = None
    description: Optional[str] = None
    authors: Optional[List[Dict[str, str]]] = None
    revision_date: Optional[str] = None
    tags: Optional[List[str]] = None
    form_number: Optional[str] = None
    form_category: Optional[str] = None
    generated: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary, excluding None values"""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                result[key] = value
        if not self.generated:
            result['generated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return result


@dataclass
class Features:
    """Interview features configuration"""
    navigation: bool = True
    progress_bar: bool = True
    progress_bar_method: Union[str, ProgressBarMethod] = ProgressBarMethod.DEFAULT
    show_progress_bar_percentage: bool = False
    navigation_back_button: bool = True
    question_back_button: bool = True
    review_button: bool = False
    hide_navbar: bool = False
    hide_standard_menu: bool = False
    css: Optional[str] = None
    table_css_class: Optional[str] = None
    bootstrap_theme: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                if isinstance(value, ProgressBarMethod):
                    result[key] = value.value
                else:
                    result[key] = value
        return result


@dataclass
class FieldDefinition:
    """Single field in a question"""
    label: str
    field: str  # Variable name
    datatype: Optional[Union[str, DataType]] = None
    required: Optional[bool] = None
    choices: Optional[List[Union[str, Dict]]] = None
    default: Optional[Any] = None
    hint: Optional[str] = None
    help_text: Optional[str] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    maxlength: Optional[int] = None
    rows: Optional[int] = None
    input_type: Optional[str] = None
    disable_others: Optional[bool] = None
    uncheck_others: Optional[bool] = None
    none_of_the_above: Optional[bool] = None
    all_of_the_above: Optional[bool] = None
    shuffle: Optional[bool] = None
    show_if: Optional[str] = None
    hide_if: Optional[str] = None
    js_show_if: Optional[str] = None
    js_hide_if: Optional[str] = None
    validate: Optional[str] = None
    validation_messages: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary, excluding None values"""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                if key == 'datatype' and isinstance(value, DataType):
                    result[key] = value.value
                elif key == 'min_value':
                    result['min'] = value
                elif key == 'max_value':
                    result['max'] = value
                elif key != 'min_value' and key != 'max_value':
                    result[key] = value
        return result


@dataclass
class Question:
    """Question block"""
    question: str
    fields: Optional[List[FieldDefinition]] = None
    subquestion: Optional[str] = None
    under: Optional[str] = None
    right: Optional[str] = None
    css: Optional[str] = None
    script: Optional[str] = None
    continue_button_field: Optional[str] = None
    continue_button_label: Optional[str] = None
    back_button: Optional[Union[bool, str]] = None
    back_button_label: Optional[str] = None
    list_collect: Optional[bool] = None
    yesno: Optional[str] = None
    noyes: Optional[str] = None
    signature: Optional[str] = None
    need: Optional[Union[str, List[str]]] = None
    depends_on: Optional[Union[str, List[str]]] = None
    reconsider: Optional[Union[bool, str, List[str]]] = None
    undefine: Optional[Union[str, List[str]]] = None
    help_text: Optional[str] = None
    terms: Optional[Dict[str, str]] = None
    auto_terms: Optional[bool] = None
    section: Optional[str] = None
    progress: Optional[Union[int, str]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {}
        
        # Always include question
        result['question'] = self.question
        
        # Add subquestion if present
        if self.subquestion:
            result['subquestion'] = self.subquestion
        
        # Convert fields
        if self.fields:
            result['fields'] = [f.to_dict() for f in self.fields]
        
        # Add other attributes
        for key, value in asdict(self).items():
            if key not in ['question', 'subquestion', 'fields'] and value is not None:
                result[key] = value
        
        return result


@dataclass
class ObjectDeclaration:
    """Object declaration"""
    name: str
    object_type: str = "DAObject"
    is_list: bool = False
    list_object_type: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        if self.is_list:
            if self.list_object_type:
                return {self.name: f"DAList.using(object_type={self.list_object_type})"}
            else:
                return {self.name: "DAList"}
        else:
            return {self.name: self.object_type}


@dataclass
class CodeBlock:
    """Code block"""
    code: str
    reconsider: Optional[Union[bool, str, List[str]]] = None
    initial: Optional[bool] = None
    mandatory: Optional[bool] = None
    need: Optional[Union[str, List[str]]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {'code': self.code}
        for key, value in asdict(self).items():
            if key != 'code' and value is not None:
                result[key] = value
        return result


@dataclass
class ReviewItem:
    """Review screen item"""
    label: str
    field: str
    edit: bool = True
    show_if: Optional[str] = None
    hide_if: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {
            'label': self.label,
            'field': self.field
        }
        if self.edit:
            result['edit'] = True
        if self.show_if:
            result['show if'] = self.show_if
        if self.hide_if:
            result['hide if'] = self.hide_if
        return result


@dataclass
class ReviewScreen:
    """Review screen"""
    review_items: List[Union[ReviewItem, Dict]]
    question: str = "Review Your Answers"
    subquestion: Optional[str] = None
    continue_button_field: Optional[str] = None
    continue_button_label: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        items = []
        for item in self.review_items:
            if isinstance(item, ReviewItem):
                items.append(item.to_dict())
            else:
                items.append(item)
        
        result = {
            'review': items,
            'question': self.question
        }
        
        if self.subquestion:
            result['subquestion'] = self.subquestion
        if self.continue_button_field:
            result['continue button field'] = self.continue_button_field
        if self.continue_button_label:
            result['continue button label'] = self.continue_button_label
            
        return result


@dataclass
class EventScreen:
    """Event/completion screen"""
    event: str
    question: str
    subquestion: Optional[str] = None
    buttons: Optional[List[Union[str, Dict]]] = None
    attachments: Optional[List[Dict]] = None
    allow_emailing: Optional[bool] = None
    allow_downloading: Optional[bool] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {
            'event': self.event,
            'question': self.question
        }
        
        for key, value in asdict(self).items():
            if key not in ['event', 'question'] and value is not None:
                result[key] = value
        
        return result


@dataclass
class MandatoryBlock:
    """Mandatory execution block"""
    code: Union[str, List[str]]
    mandatory: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        if isinstance(self.code, list):
            code_str = '\n'.join(self.code)
        else:
            code_str = self.code
        
        return {
            'mandatory': self.mandatory,
            'code': code_str
        }


@dataclass
class IncludeBlock:
    """Include dependencies"""
    includes: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {'include': self.includes}


class InterviewBuilder:
    """Builder for complete Docassemble interviews"""
    
    def __init__(self):
        self.blocks: List[Dict] = []
        self.metadata_block: Optional[Metadata] = None
        self.features_block: Optional[Features] = None
        self.includes: List[str] = []
        self.objects: List[ObjectDeclaration] = []
        self.questions: List[Question] = []
        self.code_blocks: List[CodeBlock] = []
        self.mandatory_blocks: List[MandatoryBlock] = []
        self.review_screens: List[ReviewScreen] = []
        self.event_screens: List[EventScreen] = []
    
    def set_metadata(self, metadata: Metadata) -> 'InterviewBuilder':
        """Set interview metadata"""
        self.metadata_block = metadata
        return self
    
    def set_features(self, features: Features) -> 'InterviewBuilder':
        """Set interview features"""
        self.features_block = features
        return self
    
    def add_include(self, include_path: str) -> 'InterviewBuilder':
        """Add an include file"""
        if include_path not in self.includes:
            self.includes.append(include_path)
        return self
    
    def add_object(self, obj: ObjectDeclaration) -> 'InterviewBuilder':
        """Add an object declaration"""
        self.objects.append(obj)
        return self
    
    def add_question(self, question: Question) -> 'InterviewBuilder':
        """Add a question"""
        self.questions.append(question)
        return self
    
    def add_code(self, code: CodeBlock) -> 'InterviewBuilder':
        """Add a code block"""
        self.code_blocks.append(code)
        return self
    
    def add_mandatory(self, mandatory: MandatoryBlock) -> 'InterviewBuilder':
        """Add a mandatory block"""
        self.mandatory_blocks.append(mandatory)
        return self
    
    def add_review(self, review: ReviewScreen) -> 'InterviewBuilder':
        """Add a review screen"""
        self.review_screens.append(review)
        return self
    
    def add_event(self, event: EventScreen) -> 'InterviewBuilder':
        """Add an event screen"""
        self.event_screens.append(event)
        return self
    
    def build_blocks(self) -> List[Dict]:
        """Build all blocks in proper order"""
        blocks = []
        
        # 1. Metadata (always first)
        if self.metadata_block:
            blocks.append({'metadata': self.metadata_block.to_dict()})
        
        # 2. Includes
        if self.includes:
            blocks.append(IncludeBlock(self.includes).to_dict())
        
        # 3. Features
        if self.features_block:
            blocks.append({'features': self.features_block.to_dict()})
        
        # 4. Objects
        if self.objects:
            objects_list = []
            for obj in self.objects:
                objects_list.append(obj.to_dict())
            blocks.append({'objects': objects_list})
        
        # 5. Code blocks
        for code in self.code_blocks:
            blocks.append(code.to_dict())
        
        # 6. Mandatory blocks
        for mandatory in self.mandatory_blocks:
            blocks.append(mandatory.to_dict())
        
        # 7. Questions
        for question in self.questions:
            blocks.append(question.to_dict())
        
        # 8. Review screens
        for review in self.review_screens:
            blocks.append(review.to_dict())
        
        # 9. Event screens
        for event in self.event_screens:
            blocks.append(event.to_dict())
        
        return blocks
    
    def to_yaml(self) -> str:
        """Convert to YAML string"""
        blocks = self.build_blocks()
        
        # Convert each block to YAML
        yaml_parts = []
        for block in blocks:
            yaml_part = yaml.dump(
                block,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=1000
            ).strip()
            yaml_parts.append(yaml_part)
        
        # Join with single document
        return '---\n' + '\n'.join(yaml_parts) + '\n'
    
    def to_dict(self) -> List[Dict]:
        """Get as list of dictionaries"""
        return self.build_blocks()


# Helper functions for common patterns

def create_person_object(name: str = "user", object_type: str = "Individual") -> ObjectDeclaration:
    """Create a person object"""
    return ObjectDeclaration(name=name, object_type=object_type)


def create_list_object(name: str, item_type: str = "DAObject") -> ObjectDeclaration:
    """Create a list object"""
    return ObjectDeclaration(
        name=name,
        is_list=True,
        list_object_type=item_type
    )


def create_text_field(label: str, field_name: str, required: bool = False, **kwargs) -> FieldDefinition:
    """Create a text field"""
    return FieldDefinition(
        label=label,
        field=field_name,
        datatype=DataType.TEXT,
        required=required,
        **kwargs
    )


def create_currency_field(label: str, field_name: str, required: bool = False, min_value: float = 0, **kwargs) -> FieldDefinition:
    """Create a currency field"""
    return FieldDefinition(
        label=label,
        field=field_name,
        datatype=DataType.CURRENCY,
        required=required,
        min_value=min_value,
        **kwargs
    )


def create_date_field(label: str, field_name: str, required: bool = False, **kwargs) -> FieldDefinition:
    """Create a date field"""
    return FieldDefinition(
        label=label,
        field=field_name,
        datatype=DataType.DATE,
        required=required,
        **kwargs
    )


def create_yesno_field(label: str, field_name: str, required: bool = False, **kwargs) -> FieldDefinition:
    """Create a yes/no field"""
    return FieldDefinition(
        label=label,
        field=field_name,
        datatype=DataType.YESNO,
        required=required,
        **kwargs
    )


def create_dropdown_field(label: str, field_name: str, choices: List[Union[str, Dict]], required: bool = False, **kwargs) -> FieldDefinition:
    """Create a dropdown field"""
    return FieldDefinition(
        label=label,
        field=field_name,
        choices=choices,
        required=required,
        **kwargs
    )


def create_introduction_screen(title: str, content: str, button_label: str = "Start") -> Question:
    """Create an introduction screen"""
    return Question(
        question=title,
        subquestion=content,
        continue_button_field='intro_seen',
        continue_button_label=button_label
    )


def create_completion_screen(title: str, content: str, event_name: str = "form_complete") -> EventScreen:
    """Create a completion screen"""
    return EventScreen(
        event=event_name,
        question=title,
        subquestion=content,
        buttons=[
            {'Exit': 'exit'},
            {'Start Over': 'restart'}
        ]
    )


def create_standard_features(review: bool = True, tables: bool = False) -> Features:
    """Create standard features configuration"""
    features = Features(
        navigation=True,
        progress_bar=True,
        progress_bar_method=ProgressBarMethod.STEPPED,
        show_progress_bar_percentage=True,
        navigation_back_button=True,
        question_back_button=True,
        review_button=review
    )
    
    if tables:
        features.table_css_class = "table table-striped"
    
    return features


def create_validation_code() -> str:
    """Create standard Ontario validation functions"""
    return '''# Validation functions
def validate_sin(sin):
    """Validate Canadian SIN"""
    import re
    if not sin:
        return True
    sin = re.sub(r'[^0-9]', '', sin)
    return len(sin) == 9

def validate_ontario_postal_code(postal_code):
    """Validate Ontario postal code"""
    import re
    if not postal_code:
        return True
    pattern = r'^[KLMNP]\\d[A-Z]\\s?\\d[A-Z]\\d$'
    return bool(re.match(pattern, postal_code.upper()))

def validate_phone(phone):
    """Validate phone number"""
    import re
    if not phone:
        return True
    phone_digits = re.sub(r'[^0-9]', '', phone)
    return len(phone_digits) == 10

def format_currency(amount):
    """Format currency values"""
    try:
        return f"${float(amount):,.2f}"
    except:
        return "$0.00"

def calculate_total(items, field_name='amount'):
    """Calculate total from list of items"""
    total = 0
    for item in items:
        if hasattr(item, field_name):
            total += float(getattr(item, field_name) or 0)
    return total
'''


# Example usage
if __name__ == "__main__":
    # Create a sample interview using the builder
    builder = InterviewBuilder()
    
    # Set metadata
    builder.set_metadata(Metadata(
        title="Sample Ontario Form",
        short_title="Sample Form",
        description="Example of using the structured builder",
        authors=[{"name": "Interview Builder", "organization": "Ontario Family Law"}]
    ))
    
    # Add includes
    builder.add_include("docassemble.base:data/questions/basic-questions.yml")
    
    # Set features
    builder.set_features(create_standard_features(review=True, tables=True))
    
    # Add objects
    builder.add_object(create_person_object("applicant"))
    builder.add_object(create_person_object("respondent"))
    builder.add_object(create_list_object("children", "Individual"))
    
    # Add mandatory flow
    builder.add_mandatory(MandatoryBlock(
        code=[
            "intro_seen",
            "applicant.name.first",
            "respondent.name.first",
            "review_complete",
            "form_complete"
        ]
    ))
    
    # Add introduction
    intro = create_introduction_screen(
        title="Ontario Family Law Form",
        content="This interview will help you complete your form.\n\nYou will be asked about:\n- Personal information\n- Financial details",
        button_label="Begin"
    )
    builder.add_question(intro)
    
    # Add a question with fields
    personal_question = Question(
        question="Applicant Information",
        fields=[
            create_text_field("First Name", "applicant.name.first", required=True),
            create_text_field("Last Name", "applicant.name.last", required=True),
            create_date_field("Date of Birth", "applicant.birthdate"),
            create_currency_field("Annual Income", "applicant.income", min_value=0)
        ]
    )
    builder.add_question(personal_question)
    
    # Add review screen
    review = ReviewScreen(
        review_items=[
            {"note": "### Review Your Information"},
            ReviewItem("Applicant Name", "applicant.name.first"),
            ReviewItem("Annual Income", "applicant.income")
        ],
        continue_button_field="review_complete"
    )
    builder.add_review(review)
    
    # Add completion
    builder.add_event(create_completion_screen(
        title="Form Complete",
        content="Your form is ready to submit."
    ))
    
    # Add validation code
    builder.add_code(CodeBlock(code=create_validation_code()))
    
    # Generate YAML
    print(builder.to_yaml())