from django.db import models
from django.core.exceptions import ValidationError
import ast
from django.utils.translation import gettext_lazy as _
from django import forms


def to_list(value: str):
    '''Converts stringed list to list'''
    if not isinstance(value, str):
        raise ValueError(" Argument `value` should be a string")

    try:
        value = ast.literal_eval(value)
        if not isinstance(value, list):
            raise ValidationError("Evaluated`value` is not a list")
        return value
    except:
        raise ValidationError("`value` could not be Evaluated")


def validate_text_body(value: str):
    if not isinstance(value, str):
        raise ValidationError("Invalid content item! The `body` of an item of type `text` should be a string")


def validate_list_item_body(value: dict):
    if not isinstance(value, dict):
        raise ValidationError("Invalid content item! The `body` of an item of type `list_item` should be a dictionary")
    if 1 > len(value) or len(value) > 2:
        raise ValidationError("Invalid content item! `list_item` may be containing invalid keys or is missing a key")
    
    checked = value.get('checked', None)
    item_value = value.get('item_value',None)
    if checked is not None:
        if isinstance(checked, str):
            checked = ast.literal_eval(checked)
        if not isinstance(checked, bool):
            raise ValidationError("Invalid content item! `list_item` key, 'checked', is not boolean")
            
    if not item_value:
        raise ValidationError("Invalid content item! `list_item` key, 'item_value', is required")
    if item_value and not isinstance(item_value, str):
        raise ValidationError("Invalid content item! `list_item` key, 'item_value', should be a string")


def validate_list_body(value: dict):
    if not isinstance(value, dict):
        raise ValidationError("Invalid content item! The `body` of an item of type `list` should be a dictionary")
    if len(value) != 2:
        raise ValidationError("Invalid content item! `list` has missing key(s)")
    
    title = value.get('title', None)
    list_items = value.get('list_items', None)
    if not title:
        raise ValidationError("Invalid content item! `list` key, 'title', is required")
    if not list_items:
        raise ValidationError("Invalid content item! `list` key, 'list_items', is required")

    if not isinstance(title, str):
        raise ValidationError("Invalid content item! `list` key, 'title', is not a string")
    if not isinstance(list_items, list):
        raise ValidationError("Invalid content item! `list` key, 'list_items', is not a list")

    for item in list_items:
        if not isinstance(item, dict):
            raise ValidationError("Invalid list item")

        _type: str = item.get('type', None)
        _body: dict = item.get('body', None)
        
        if not _body:
            raise ValidationError("list item should have 'body' attribute")
        if not _type:
            raise ValidationError("list item should have 'type' attribute")
        if not isinstance(_type, str):
            raise ValidationError("list item 'type' attribute should be a string")
        if not _type.lower() == "list_item":
            raise ValidationError("list item 'type' attribute is invalid")

        validate_list_item_body(_body)
    

def validate_note_content(content: list[dict] | str, allowed_types: list):
    '''Validates a `NoteContent` object's content and returns it.'''
    if not isinstance(content, (list, str)):
        raise ValidationError("Invalid content type: {}".format(type(content)))

    if isinstance(content, str):
        if not isinstance(ast.literal_eval(content), (str, list)):
            raise ValidationError("Invalid content type: {}".format(type(ast.literal_eval(content))))
        else:
            content = to_list(content)

    for content_item in content:
        if not isinstance(content_item, dict):
            raise ValidationError("Invalid content item")

        _type: str = content_item.get('type', None)
        if not _type:
            raise ValidationError("content item should have 'type' attribute")
        if not isinstance(_type, str):
            raise ValidationError("content item 'type' attribute should be a string")
        
        _body = content_item.get('body', None)
        if not _body:
            raise ValidationError("content item type `%s` should have 'body' attribute" % _type)

        if _type and _type.lower() in allowed_types:
            match _type.lower():
                case "text":
                    validate_text_body(_body)
                
                case "list_item":
                    validate_list_item_body(_body)

                case "list":
                    validate_list_body(_body)
    return content
        
INITIAL_CONTENT_FORMAT = [
    {
        "type": "text",
        "body": "<str>",
    },

    {
        "type": "list_item",
        "body": {
            "checked": False,
            "item_value": "<str>",
        },
    },

    {
        "type": "list",
        "body": {
            "title": "<str>",
            "list_items": [
                {
                    "type": "list_item",
                    "body": {
                        "checked": False,
                        "item_value": "<str>",
                    },
                },
                {
                    "type": "list_item",
                    "body": {
                        "checked": False,
                        "item_value": "<str>",
                    },
                },
            ],
        },
    }, 
]



class NoteContent:
    '''Class used to create instances for storing the content of `Note` model objects'''
    allowed_content_types = ['text', 'list', 'list_item']

    def __init__(self, content: list):
        self.content = validate_note_content(content=content, allowed_types=self.allowed_content_types)

    def __repr__(self):
        return f"NoteContent: {self.__dict__()}"

    def __str__(self):
       return f"{self.content}"

    def __dict__(self):
        obj = {
            "content": self.content,
            "details": self.details,
        }
        return obj

    def __getitem__(self):
        return self.__dict__()


    def __iter__(self):
        return self

    def next(self):
        x = 0
        if x < len(self.content):
            x += 1
            return self.content[x - 1]
        else:
            StopIteration

    def __setattr__(self, __name: str, __value):
        if __name == "content":
            if isinstance(__value, str):
                __value = validate_note_content(content=__value, allowed_types=self.allowed_content_types)

        if __name == "allowed_content_types":
            if not isinstance(__value, (list, tuple)):
                TypeError("Invalid type: {} for `allowed_content_types` attribute".format(type(__value)))

        return super().__setattr__(__name, __value)

    @property
    def text_contents(self):
        text_contents = []
        for content in self.content:
            if content.get('type').lower() == "text":
                text_contents.append(content)
        return text_contents

    @property
    def list_items(self):
        list_items = []
        for content in self.content:
            if content.get('type').lower() == "list_item":
                list_items.append(content)
        return list_items

    @property
    def lists(self):
        lists = []
        for content in self.content:
            if content.get('type').lower() == "list":
                lists.append(content)
        return lists

    @property
    def texts_count(self) -> int:
        return len(self.text_contents)

    @property
    def list_items_count(self) -> int:
        count = len(self.list_items) 
        for list in self.lists:
            count += len(list['body']['list_items'])
        return count

    @property
    def lists_count(self) -> int:
        return len(self.lists)

    @property
    def approximate_word_count(self) -> int:
        count = 0
        texts = self.text_contents
        list_items = self.list_items
        lists = self.lists

        for text in texts:
            count += len((text.get('body')).split('\s'))
        
        for list_item in list_items:
            count += len((list_item['body']['item_value']).split('\s'))

        for list in lists:
            count += len((list['body']['title']).split('\s'))
            for item in list['body']['list_items']:
                count += len((item['body']['item_value']).split('\s'))
        return count

    @property
    def details(self):
        details = {
            "no_of_text_content": self.texts_count,
            "no_of_list_items": self.list_items_count,
            "no_of_lists": self.lists_count,
            "approximate_word_count": self.approximate_word_count,
        }
        return details


        


class NoteContentField(models.TextField):
    description = _("Field that stores a `NoteContent`")

    def __init__(self, *args, **kwargs):
        if not kwargs.get('default', None):
            kwargs.update({"default": INITIAL_CONTENT_FORMAT})

        if not kwargs.get('help_text', None):
            kwargs.update({"help_text": "Construct your note content using the default format provided in the field."})
        return super().__init__(*args, **kwargs)

    def db_type(self, connection) -> str:
        return super().db_type(connection)

    def from_db_value(self, value, expression, connection) -> NoteContent:
        if value is None:
            return value
        return NoteContent(value)

    def to_python(self, value) -> NoteContent:
        if isinstance(value, NoteContent):
            return value

        if value is None:
            return value
        return NoteContent(value)

    def validate(self, value, model_instance):
        try:
            _ = NoteContent(value)
        except ValidationError:
            raise ValidationError("value provided is invalid")


    def get_prep_value(self, value) -> str:
        if value is None:
            return value
        return NoteContent(value).__str__()

    def get_db_prep_value(self, value, connection, prepared=False) -> str:
        return super().get_db_prep_value(value, connection, prepared)


    def value_to_string(self, obj) -> str:
        value = self.value_from_object(obj)
        if isinstance(value, NoteContent):
            return value.__str__()
        return self.get_prep_value(value)


    def formfield(self, **kwargs):
        kwargs.update({'form_class': forms.JSONField})
        return super().formfield(**kwargs)