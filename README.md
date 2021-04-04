# Ziggurat 

A simple and straightforward Python templating engine.

![CI](https://github.com/rsiemens/ziggurat/actions/workflows/ci.yml/badge.svg?branch=master)

### A Quick Example

```
Dunder Mifflin Sales Report
---------------------------

{ branch | capitalize} - {quarter} {year}

@if confidential@
Private Information, do not share!
@endif@

Product    Sold    Amount
@for product in sales@
{product.name}  {product.sold}  {product.amount | with_dollar_sign}
@endfor@
```

```python
from ziggurat import Template, register_transform

@register_transform
def with_dollar_sign(value):
    return f'${value:.2f}'

report = Template('report.txt').render({
    'branch': 'scranton',
    'quarter': 'Q1',
    'year': 2021,
    'confidential': True,
    'sales': [
        {'name': 'Letter 8.5" x 11"', 'sold': 500, 'amount': 8975},
        {'name': 'Legal 8.5" x 14"', 'sold': 237, 'amount': 7107},
    ]
})

print(report)
```

```
Dunder Mifflin Sales Report
---------------------------

Scranton - Q1 2021

Private Information, do not share!

Product    Sold    Amount
Letter 8.5" x 11"  500  $8975.00
Legal 8.5" x 14"  237  $7107.00
```

### Features

#### `{variable}` lookup

Looks up the variable passed into the `Template.render` context dictionary and replaces it with the string value.

```
Hello {name}!
```

If `variable` is a dictionary or an object you can access members using `.` notation.

```
Hello {user.name}
```

#### `{variable | transform}` transforms

Passes `variable` to the registered `transform` function. `transform` is a function which takes a single argument, the value of `variable`, and return a value.
You can also chain transforms allowing for a more complex transform constructed from many smaller ones. If the value of the variable, or last transform, is not
a string, then an implicit `str(value)` transform is applied.

For example, registering a `reverse` transform

```python
from ziggurat import Template, register_transform

@register_transform
def reverse(value):
    return value[::-1]

Template('greeting.txt').render({'name': 'World'})
```

Which could then be used in `greeting.txt` like so

```
Hello {name|reverse}!
```

producing `Hello dlroW!`.

You can also chain transforms

```
Hello {name | reverse | lower | capitalize}!
```

producing `Hello Dlrow!`.

#### `@if condition@` statement

Used to conditionally render some text.

```
@if name@
Hello {name}!
@endif@
```

You can also pair it with an `@else@` to provide an alternative.

```
@if name@
Hello {name}!
@else@
Hello!
@endif@
```

If `condition` is a dictionary or an object you can access members using `.` notation.

```
@if user.name@Hello {user.name}@endif@
```

#### `@for item in collection@` iterator

Used for looping over a collection.

```
@for city in cities@
- {city}
@endfor@
```

#### `@include template@` directive

Useful for transcluding a common piece of template into another template. For example consider a simple letterhead that is always included in documents.

```
Big Business Inc.
{phone}
{email}
{address}

To: {to}
Date: {date}
```

This can then be included in all letters like so.

```
@include letterhead.txt@

Dear {to},

Thanks for doing big business with Big Business Inc!

Best Regards,

{from}
```

The included template will have the same context available to it as the parent template.
