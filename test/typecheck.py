from typing import get_type_hints, Any
from functools import wraps
from inspect import getfullargspec
import traceback


def match_return(all_required, all_results):
    if len(all_required) != len(all_results):
        # raise error if number of requirements and return is not match
        raise TypeError(
            'Number of return Argument and required is not match')
    for requirements, result in zip(all_required, all_results):
        # print(requirements, result)
        if requirements is None:
            if result is not None:
                raise TypeError(
                    'Return value %r is not of type %s' % (
                        result, requirements)
                )
        elif requirements != Any and not isinstance(result, requirements):
            # print(requirements, result)
            raise TypeError(
                'Return value %r is not of type %s' % (
                    result, requirements)
            )

def validate_input(func, **kwargs):
    hints = get_type_hints(func)
    # print(hints)
    #get all type of result function
    all_results = func(**kwargs)
    try:
        len(all_results)
    except:
        all_results = (all_results,)

    # print('all_results', all_results)
    # iterate all type hints
    for attr_name, attr_type in hints.items():
        if attr_name == 'return':
            # get all type of requirement
            all_required = hints['return']
            try:
                len(all_required)
            except:
                all_required = (all_required,)
            match_return(all_required, all_results)
        elif attr_type!=Any and not isinstance(kwargs[attr_name], attr_type):
            raise TypeError(
                'Argument %r = %r is not of type %s' % (attr_name, kwargs[attr_name], attr_type)
            )
    if len(all_results)==1:
        return all_results[0]
    else:
        return all_results


def type_check(decorator):
    """Function check all type of input argument and return value of 'def' as specified in typing module (from python 3.3). It will raise Type Error if any wrong type.
    
    Arguments:
        decorator {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """

    @wraps(decorator)
    def wrapped_decorator(*args, **kwargs):
        # translate *args into **kwargs
        func_args = getfullargspec(decorator)[0]
        default_kwargs = getfullargspec(decorator).defaults
        kwargs.update(dict(zip(func_args, args)))
        # update default value
        func_defaults = [arg for arg in func_args if arg not in kwargs]
        kwargs.update(dict(zip(func_defaults, default_kwargs)))
        # print('func_args=', func_args, 'kwargs=', kwargs)
        return validate_input(decorator, **kwargs)

    return wrapped_decorator


class ArgumentValidationError(ValueError):
    '''
    Raised when the type of an argument to a function is not what it should be.
    '''

    def __init__(self, arg_num, func_name, accepted_arg_type):
        self.error = 'The {0} argument of {1}() is not a {2}'.format(arg_num,
                                                                     func_name,
                                                                     accepted_arg_type)

    def __str__(self):
        return self.error


class InvalidArgumentNumberError(ValueError):
    '''
    Raised when the number of arguments supplied to a function is incorrect.
    Note that this check is only performed from the number of arguments
    specified in the validate_accept() decorator. If the validate_accept()
    call is incorrect, it is possible to have a valid function where this
    will report a false validation.
    '''

    def __init__(self, func_name):
        self.error = 'Invalid number of arguments for {0}()'.format(func_name)

    def __str__(self):
        return self.error


class InvalidReturnType(ValueError):
    '''
    As the name implies, the return value is the wrong type.
    '''

    def __init__(self, return_type, func_name):
        self.error = 'Invalid return type {0} for {1}()'.format(return_type,
                                                                func_name)

    def __str__(self):
        return self.error


def ordinal(num):
    '''
    Returns the ordinal number of a given integer, as a string.
    eg. 1 -> 1st, 2 -> 2nd, 3 -> 3rd, etc.
    '''
    if 10 <= num % 100 < 20:
        return '{0}th'.format(num)
    else:
        ord = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
        return '{0}{1}'.format(num, ord)


def accepts(*accepted_arg_types):
    '''
    A decorator to validate the parameter types of a given function.
    It is passed a tuple of types. eg. (<type 'tuple'>, <type 'int'>)

    Note: It doesn't do a deep check, for example checking through a
          tuple of types. The argument passed must only be types.
    '''

    def accept_decorator(validate_function):
        # Check if the number of arguments to the validator
        # function is the same as the arguments provided
        # to the actual function to validate. We don't need
        # to check if the function to validate has the right
        # amount of arguments, as Python will do this
        # automatically (also with a TypeError).
        @wraps(validate_function)
        def decorator_wrapper(*function_args, **function_args_dict):
            if len(accepted_arg_types) is not len(function_args):
                raise InvalidArgumentNumberError(validate_function.__name__)

            # We're using enumerate to get the index, so we can pass the
            # argument number with the incorrect type to ArgumentValidationError.
            for arg_num, (actual_arg, accepted_arg_type) in enumerate(zip(function_args, accepted_arg_types)):
                if not type(actual_arg) is accepted_arg_type:
                    ord_num = ordinal(arg_num + 1)
                    raise ArgumentValidationError(ord_num,
                                                  validate_function.__name__,
                                                  accepted_arg_type)

            return validate_function(*function_args)
        return decorator_wrapper
    return accept_decorator


def returns(*accepted_return_type_tuple):
    '''
    Validates the return type. Since there's only ever one
    return type, this makes life simpler. Along with the
    accepts() decorator, this also only does a check for
    the top argument. For example you couldn't check
    (<type 'tuple'>, <type 'int'>, <type 'str'>).
    In that case you could only check if it was a tuple.
    '''
    def return_decorator(validate_function):
        # No return type has been specified.
        if len(accepted_return_type_tuple) == 0:
            raise TypeError('You must specify a return type.')

        @wraps(validate_function)
        def decorator_wrapper(*function_args):
            # More than one return type has been specified.
            if len(accepted_return_type_tuple) > 1:
                raise TypeError('You must specify one return type.')

            # Since the decorator receives a tuple of arguments
            # and the is only ever one object returned, we'll just
            # grab the first parameter.
            accepted_return_type = accepted_return_type_tuple[0]

            # We'll execute the function, and
            # take a look at the return type.
            return_value = validate_function(*function_args)
            return_value_type = type(return_value)

            if return_value_type is not accepted_return_type:
                raise InvalidReturnType(return_value_type,
                                        validate_function.__name__)

            return return_value

        return decorator_wrapper
    return return_decorator


@accepts(int, int)
@returns(int)
def add_nums_correct(a, b):
    '''
    Adds two numbers. It accepts two
    integers, and returns an integer.
    '''

    return a + b


@accepts(int, int)
@returns(int)
def add_nums_incorrect(a, b):
    '''
    Adds two numbers. It accepts two
    integers, and returns an integer.
    '''

    return 'Not an int!'


def main():
    @type_check
    def checkstr(s: str='something')->(Any, str):
        return None, s

    @type_check
    def a_plus_b(a:int, b:int=0)->(int):
        return a+b
    
    @type_check
    def plusabc(a: int, b: int=1, c:int=2)->(int):
        return a+b+c
    
    @type_check
    def return_none(a: int, b: int=1, c: int=2)->(None):
        print('a+b+c=', a+b+c)

    x,y = checkstr('tuan')
    print(x,y)
    z = a_plus_b(10,30)
    print(z)
    z2 = a_plus_b(1)
    print(z2)
    print(plusabc(0))
    print(return_none(12))
    # try:
    #     checkstr(120)
    # except Exception as error:
    #     print(error)
    #     traceback.print_exc()
    # # That will raise an error of TypeError
    # checkstr(200)
    # print(checkstr(20))


if __name__ == '__main__':
    main()
