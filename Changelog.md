# Changelog

## 0.6.1

- Fix not forwarding leave_none in as_dict

## 0.6.0

- `as_dict` now has optional `leave_none` boolean parameter to allow field with None as value to be in output, False by default

## 0.5.1

 - Fix not making Scheme field into dict when `as_dict` is called and field is aliased

## 0.5.0

- Optional field class, a shortcut for `Field(type(None), ...)`

## 0.4.1

- Fix bug when structeres were not mapped when only scheme names were fiven as Field types

## 0.4.0

- Scheme name can be used to define recursive structure

## 0.3.1

- Impovements in aliases

## 0.3.0

- Field aliases support

## v0.2.0

- multiple field types are now passed as *args, which somewhat simplifies code
- added support for validators

## v0.1.0

- Basic mapping of dictionaries to python objects
