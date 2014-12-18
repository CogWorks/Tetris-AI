//TODO: this file needs a whole lot of comments!

#include <memory>

#include <stdlib.h>

#include <Python.h>

#include "tetris_cow.hpp"

#define DEFAULT_CACHE_SIZE 1000


//typedefs for the 20x10 statically-sized board

typedef tetris_cow <int[20][10]>         tetris_20_10;
typedef tetris_20_10                    *tetris_20_10_pointer;
typedef tetris_20_10::row_cache          row_cache;
typedef tetris_20_10::row_cache_pointer  row_cache_pointer;


//a cache for storing rows that have been discarded

const row_cache_pointer &get_row_cache(size_t limit = 0) {
  static tetris_20_10::row_type default_row = {0,0,0,0,0,0,0,0,0,0};
  static row_cache_pointer cache;

  if (!cache) cache.reset(new row_cache(limit, default_row));
  else if (limit) cache->set_limit(limit);

  return cache;
}


//the module object for 'tetris_cpp'

static PyObject *module = NULL;


//some helper functions for the python bindings

static inline PyObject __attribute__ ((warn_unused_result)) *auto_exception(PyObject *exception,
  const char *message) {
  PyErr_SetString(exception, message);
  return NULL;
}

static inline int __attribute__ ((warn_unused_result)) auto_exception2(PyObject *exception,
  const char *message) {
  PyErr_SetString(exception, message);
  return -1;
}

static inline PyObject __attribute__ ((warn_unused_result)) *use_object(PyObject *object) {
  Py_INCREF(object);
  return object;
}

void add_global_binding(PyMethodDef *binding) {
  PyObject *new_function = PyCFunction_New(binding, NULL);
  if (!new_function) return;
  PyObject_SetAttrString(module, binding->ml_name, new_function);
}


//some macros for redundant binding code

#define GLOBAL_BINDING_START(name, doc) \
const char name##_doc[] = doc; \
static PyObject *name##_function(PyObject *self, PyObject *args, PyObject *kwds) {

#define GLOBAL_BINDING_END(name) } \
static PyMethodDef name##_binding = {#name, (PyCFunction) &name##_function, METH_KEYWORDS, name##_doc};

#define METHOD_BINDING_START(name, doc) \
const char python_tetris_20_10_##name##_doc[] = doc; \
static PyObject *python_tetris_20_10_##name##_function(python_tetris_20_10 *self, PyObject *args, PyObject *kwds) {

#define METHOD_BINDING_END(name) }

#define METHOD_BINDING(name) \
METHOD_BINDING2(name, name)

#define METHOD_BINDING2(name, name2) \
{ #name2, (PyCFunction) python_tetris_20_10_##name##_function, METH_VARARGS, python_tetris_20_10_##name##_doc }


//global functions for getting/setting the cache size

GLOBAL_BINDING_START(set_cache_size, "set the size of the row cache")
  int count = 0;
  if(!PyArg_ParseTuple(args, "i", &count)) return NULL;
  if (count < 0) return auto_exception(PyExc_ValueError, "value must be a positive integer");
  get_row_cache(count);
  return Py_BuildValue("");
GLOBAL_BINDING_END(set_cache_size)

GLOBAL_BINDING_START(get_cache_size, "get the size of the row cache")
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", (int) (get_row_cache()? get_row_cache()->get_limit() : 0));
GLOBAL_BINDING_END(get_cache_size)


//the 'tetris_20_10' class

typedef struct { \
  PyObject_HEAD \
  tetris_20_10_pointer obj; \
} python_tetris_20_10;

static PyTypeObject python_tetris_20_10_type = {
  PyObject_HEAD_INIT(NULL)
};


//'tetris_20_10' member functions

static int python_tetris_20_10_init_function(python_tetris_20_10 *self, PyObject *args, PyObject *kwds) {
  int count = 0;
  if(!PyArg_ParseTuple(args, "|i", &count)) return -1;
  if (!self->obj) {
    self->obj = new tetris_20_10(get_row_cache(), count);
    if (!self->obj) return auto_exception2(PyExc_RuntimeError, "could not allocate board");
  }
  if (count < 0 || count > 20) return auto_exception2(PyExc_ValueError, "invalid number of rows");
  self->obj->add_rows(count - (int) self->obj->pile_height());
  return 0;
}

static void python_tetris_20_10_dealloc_function(python_tetris_20_10 *self) {
  delete self->obj;
  self->obj = NULL;
}

METHOD_BINDING_START(clone, "clone another board")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  python_tetris_20_10 *other = NULL;
  if (!PyArg_ParseTuple(args, "O!", &python_tetris_20_10_type, &other)) return NULL;
  if (!other->obj) {
    other->obj = new tetris_20_10(get_row_cache());
    if (!other->obj) return auto_exception(PyExc_ValueError, "");
  }
  *self->obj = *other->obj;
  return Py_BuildValue("");
METHOD_BINDING_END(row_count)

PyObject *python_tetris_20_10_getitem_function(python_tetris_20_10 *self, PyObject *key) {
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  int r = 0, c = 0;
  if(!PyArg_ParseTuple(key, "ii", &r, &c)) return NULL;
  if (r < 0 || r >= (signed) self->obj->row_count()) return auto_exception(PyExc_IndexError, "index out of range");
  if (c < 0 || c >= (signed) self->obj->col_count()) return auto_exception(PyExc_IndexError, "index out of range");
  return Py_BuildValue("i", (int) self->obj->get_cell(r, c));
}

int python_tetris_20_10_setitem_function(python_tetris_20_10 *self, PyObject *key, PyObject *val) {
  if (!self->obj) return auto_exception2(PyExc_RuntimeError, "");
  int r = 0, c = 0, value = 0;
  if(!PyArg_ParseTuple(key, "ii", &r, &c)) return -1;
  value = PyInt_AsLong(val);
  if (value == -1 && PyErr_Occurred()) return -1;
  if (r < 0 || r >= (signed) self->obj->pile_height()) return auto_exception2(PyExc_IndexError, "index out of range");
  if (c < 0 || c >= (signed) self->obj->col_count())   return auto_exception2(PyExc_IndexError, "index out of range");
  self->obj->set_cell(r, c, value);
  return 0;
}

METHOD_BINDING_START(row_count, "get the number of rows")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", (int) self->obj->row_count());
METHOD_BINDING_END(row_count)

METHOD_BINDING_START(col_count, "get the number of cols")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", (int) self->obj->col_count());
METHOD_BINDING_END(col_count)

METHOD_BINDING_START(pile_height, "get the pile height")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", (int) self->obj->pile_height());
METHOD_BINDING_END(pile_height)

METHOD_BINDING_START(add_rows, "add rows to the pile")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  int count = 0;
  if(!PyArg_ParseTuple(args, "i", &count)) return NULL;
  return Py_BuildValue("i", (int) self->obj->add_rows(count));
METHOD_BINDING_END(add_rows)

METHOD_BINDING_START(is_fake_row, "check if a row is faked")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  int r = 0;
  if(!PyArg_ParseTuple(args, "i", &r)) return NULL;
  if (r < 0 || r >= (signed) self->obj->row_count()) return auto_exception(PyExc_IndexError, "index out of range");
  return use_object(self->obj->is_fake_row(r)? Py_True : Py_False);
METHOD_BINDING_END(is_fake_row)

METHOD_BINDING_START(is_mirrored_row, "check if a row is mirrored")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  int r = 0;
  if(!PyArg_ParseTuple(args, "i", &r)) return NULL;
  if (r < 0 || r >= (signed) self->obj->row_count()) return auto_exception(PyExc_IndexError, "index out of range");
  return use_object(self->obj->is_mirrored_row(r)? Py_True : Py_False);
METHOD_BINDING_END(is_mirrored_row)

METHOD_BINDING_START(check_full, "check if any rows are full, optionally removing them")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  PyObject *clear = Py_False;
  if(!PyArg_ParseTuple(args, "|O", &clear)) return NULL;
  return Py_BuildValue("i", (int) self->obj->check_full(PyObject_IsTrue(clear)));
METHOD_BINDING_END(check_full)

METHOD_BINDING_START(check_empty, "check if any rows are empty, optionally removing them")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  PyObject *clear = Py_False;
  if(!PyArg_ParseTuple(args, "|O", &clear)) return NULL;
  return Py_BuildValue("i", (int) self->obj->check_empty(PyObject_IsTrue(clear)));
METHOD_BINDING_END(check_empty)

METHOD_BINDING_START(set_tamper_seal, "set the state of the tamper seal")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  PyObject *state = Py_True;
  if(!PyArg_ParseTuple(args, "|O", &state)) return NULL;
  self->obj->set_tamper_seal(PyObject_IsTrue(state));
  return Py_BuildValue("");
METHOD_BINDING_END(pile_height)

METHOD_BINDING_START(get_tamper_seal, "get the state of the tamper seal")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return use_object(self->obj->get_tamper_seal()? Py_True : Py_False);
METHOD_BINDING_END(pile_height)


//list of all 'tetris_20_10' member functions

static PyMethodDef python_tetris_20_10_methods[] = {
  METHOD_BINDING(clone),
  METHOD_BINDING(row_count),
  METHOD_BINDING(col_count),
  METHOD_BINDING(pile_height),
  METHOD_BINDING(add_rows),
  METHOD_BINDING(is_fake_row),
  METHOD_BINDING(is_mirrored_row),
  METHOD_BINDING(check_full),
  METHOD_BINDING(check_empty),
  METHOD_BINDING(set_tamper_seal),
  METHOD_BINDING(get_tamper_seal)
};


//__getitem__/__setitem__ for 'tetris_20_10'

static PyMappingMethods python_tetris_20_10_mapping = {
  .mp_length        = NULL,
  .mp_subscript     = (binaryfunc) &python_tetris_20_10_getitem_function,
  .mp_ass_subscript = (objobjargproc) &python_tetris_20_10_setitem_function
};


//initialization function, called when loading from python

extern "C" {
PyMODINIT_FUNC inittetris_cpp(void);
}

PyMODINIT_FUNC init_tetris_cpp(void) {
  PyEval_InitThreads();
  module = Py_InitModule3("_tetris_cpp", NULL, "");
  if (!module) return;

  //NOTE: these aren't assigned in the initializer because that would require
  //that they be in the right order, etc.
  python_tetris_20_10_type.tp_name       = "tetris_20_10";
  python_tetris_20_10_type.tp_basicsize  = sizeof(python_tetris_20_10);
  python_tetris_20_10_type.tp_dealloc    = (destructor) &python_tetris_20_10_dealloc_function;
  python_tetris_20_10_type.tp_doc        = "";
  python_tetris_20_10_type.tp_as_mapping = &python_tetris_20_10_mapping;
  python_tetris_20_10_type.tp_flags      = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;
  python_tetris_20_10_type.tp_methods    = python_tetris_20_10_methods;
  python_tetris_20_10_type.tp_init       = (initproc) &python_tetris_20_10_init_function;
  python_tetris_20_10_type.tp_new        = PyType_GenericNew;
  python_tetris_20_10_type.tp_getattro   = PyObject_GenericGetAttr;

  //add the 'tetris_20_10' class
  if (PyType_Ready(&python_tetris_20_10_type) < 0) return;
  Py_INCREF(&python_tetris_20_10_type);
  if (PyModule_AddObject(module, "tetris_20_10", (PyObject*) &python_tetris_20_10_type) < 0) return;

  //set the initial cache size
  get_row_cache(DEFAULT_CACHE_SIZE);

  add_global_binding(&set_cache_size_binding);
  add_global_binding(&get_cache_size_binding);
}
