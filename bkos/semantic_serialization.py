import ast
import inspect
from typing import TypeVar

import bkos.ontology


permitted_classes = None
permitted_type_vars = None


def register_module(module):
    global permitted_classes, permitted_type_vars
    for name in vars(module).keys():
        value = getattr(module, name)
        if inspect.isclass(value):
            if issubclass(value, bkos.ontology.SemanticClass):
                permitted_classes[name] = value
        elif isinstance(value, TypeVar):
            permitted_type_vars[name] = value


def initialize():
    global permitted_classes, permitted_type_vars
    permitted_classes = {}
    permitted_type_vars = {}
    register_module(bkos.ontology)


initialize()


class DeserializationException(Exception):
    pass


class BuildException(Exception):
    pass


def deserialize(string):
    try:
        module = ast.parse(string)
    except Exception as parse_exception:
        raise DeserializationException(
            f'Exception occurred when parsing {string!r}: {parse_exception}')
    try:
        return build(module.body[0])
    except BuildException as build_exception:
        raise DeserializationException(
            f'Exception occurred when building deserialization for {string!r}: {build_exception}')


def build(node):
    if isinstance(node, list):
        return [build(element) for element in node]
    if isinstance(node, ast.List):
        return [build(element) for element in node.elts]
    if isinstance(node, ast.Expr):
        return build(node.value)
    if isinstance(node, ast.Call):
        functor = node.func.id
        if functor in permitted_classes:
            class_ = permitted_classes[functor]
            built_args = build(node.args)
            built_kwargs = dict(build(node.keywords))
            try:
                return class_(*built_args, **built_kwargs)
            except Exception as exception:
                raise BuildException(
                    f'Exception when trying to create instance of {functor} with arguments {built_args}: {exception}')
        else:
            raise BuildException(f'Expected a permitted class for {node} but got {functor!r}')
    if isinstance(node, ast.Name):
        if node.id in permitted_type_vars:
            return permitted_type_vars[node.id]
        elif node.id in permitted_classes:
            return permitted_classes[node.id]
        else:
            raise BuildException(f'Expected a permitted class or individual for {node} but got {node.id!r}')
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.keyword):
        return node.arg, build(node.value)
    raise BuildException(f'Failed to build node {node!r}')
