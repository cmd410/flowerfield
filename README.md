# FlowerField

Tiny python module to automatically map dictionaries to python objects.

## Installation

### Pypi

Install with python's package manager:

```
pip install flowerfield
```

### Git

```
pip intall git+https://github.com/cmd410/flowerfield.git
```

### Or...

*...or just copy __flowerfield__ directory into your project, this module doesn't depend on anything*

## Usage

This library is stupid simple to use:

```python
from flowerfield import Scheme, Field, ListField
from enum import Enum


class FlowerType(str, Enum):
    DANDELION = 'Dandelion'
    SUNFLOWER = 'Sunflower'
    ROSE = 'Rose'


class MyThing(Scheme, root=True):
    pass


class Flower(MyThing):
    color = Field(str, tuple)
    type = Field(str, validator=FlowerType)


class Pot(MyThing):
    flowers = ListField(Flower)
    watered = Field(bool)


print(MyThing.from_dict(
        {
            'flowers': [
                    {'color': '#fa21aa',
                     'type': 'Dandelion'},
                    {'color': '#daf1ad',
                     'type': 'Sunflower'},
                    {'color': '#ffaadd',
                     'type': 'Rose'}
            ],
            'watered': False
        }
    )
)

# Output:
# Pot(flowers=[Flower(type=<FlowerType.DANDELION: 'Dandelion'>, color='#fa21aa'), Flower(type=<FlowerType.SUNFLOWER: 'Sunflower'>, color='#daf1ad'), Flower(type=<FlowerType.ROSE: 'Rose'>, color='#ffaadd')], watered=False)
```

First we create a class `MyThing` which inherits from `Scheme` and has a keyword parameter `root`. This parameter is a boolean which, when true means that this class will be used to map its children. Root Schemes are a way to organize you schemes into some categories that you want to match dictionaries against. Root schemes never participate in the match themselves, adding fields to them is pointless.

> Scheme is a root itself, so when you call `Scheme.from_dict(some_dictionary)` it will return most suitable scheme object from ALL its children that exist in you program.

Next we create `Flower` and `Pot` class and add some fields to them. Field class, optionally accepts type of the field it will check against when set. You can give more than one type as tuple. Schemes as fields type automatically map every dictionary that is given to that field. You can make Optional fields by passing `type(None)` into Field.

Flower class has a `validator` in `type` field. Validators are callables that accept value of the field and return validated value or raise an exception.

Then we call `MyThing.from_dict(...)` and it automatically creates a Pot with Flowers inside of it based the dict we gave it. Isn't that nice?

You can, of course, call `from_dict` on non-root scheme but it will only map this concrete scheme.

### How it determines what schema to use?

When deciding to what class to map a dictionary it goes through following steps:

1. Get keys from dictionary
2. Go through subclasses and check how much of fields names intersect with dictionary keys
3. Choose a structure which has the most keys in it.