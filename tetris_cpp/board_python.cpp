//TODO: this file needs a whole lot of comments!

#include <stack>
#include <memory>

#include <stdlib.h>

#include <Python.h>

#include "tetris_cow.hpp"

#define DEFAULT_ROW_CACHE_SIZE   500
#define DEFAULT_BOARD_CACHE_SIZE 25


//typedefs for the 20x10 board

#ifndef DYNAMIC
typedef tetris_cow <int[20][10]>         tetris_20_10;
#else
typedef tetris_cow <int>                 tetris_20_10;
#endif
typedef tetris_20_10                    *tetris_20_10_pointer;
typedef tetris_20_10::row_cache          row_cache;
typedef tetris_20_10::row_cache_pointer  row_cache_pointer;


//a cache for storing rows that have been discarded

const row_cache_pointer &get_row_cache(ssize_t limit = -1) {
#ifndef DYNAMIC
  static tetris_20_10::row_type default_row = {0,0,0,0,0,0,0,0,0,0};
#else
  static tetris_20_10::row_type default_row(10);
#endif
  static row_cache_pointer cache;

  if (!cache) cache.reset(new row_cache((limit < 0)? 0 : limit, default_row));
  else if (limit >= 0) cache->set_limit(limit);

  return cache;
}


//cache for board objects

typedef std::unique_ptr <tetris_20_10>   tetris_20_10_cached;
typedef std::stack <tetris_20_10_cached> tetris_20_10_cache;

static tetris_20_10_cache board_cache;
static size_t board_cache_limit = DEFAULT_BOARD_CACHE_SIZE;

static void cache_board(tetris_20_10_pointer board) {
  if (!board) return;
  if (board_cache.size() >= board_cache_limit) {
    delete board;
  }
  else {
    board->clear_all();
    board_cache.push(tetris_20_10_cached());
    board_cache.top().reset(board);
  }
}

static tetris_20_10_pointer uncache_board(size_t count = 0) {
  if (board_cache.size()) {
    tetris_20_10_pointer board = board_cache.top().release();
    board_cache.pop();
    assert(board);
    board->add_rows(count);
    return board;
  } else {
#ifndef DYNAMIC
    return new tetris_20_10(get_row_cache(), count);
#else
    return new tetris_20_10(get_row_cache(), 20, 10, count);
#endif
  }
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

#define METHOD_BINDING_START(type, name, doc) \
const char python_##type##_##name##_doc[] = doc; \
static PyObject *python_##type##_##name##_function(python_##type *self, PyObject *args, PyObject *kwds) {

#define METHOD_BINDING_END(type, name) }

#define METHOD_BINDING(type, name) \
METHOD_BINDING2(type, name, name)

#define METHOD_BINDING2(type, name, name2) \
{ #name2, (PyCFunction) python_##type##_##name##_function, METH_KEYWORDS, python_##type##_##name##_doc }


//global functions for getting/setting the cache sizes

GLOBAL_BINDING_START(set_row_cache_size, "set the size of the row cache")
  int count = 0;
  static char *keywords[] = { "max", NULL };
  if(!PyArg_ParseTupleAndKeywords(args, kwds, "i", keywords, &count)) return NULL;
  if (count < 0) return auto_exception(PyExc_ValueError, "value must be a positive integer");
  get_row_cache(count);
  return Py_BuildValue("");
GLOBAL_BINDING_END(set_row_cache_size)

GLOBAL_BINDING_START(get_row_cache_size, "get the size of the row cache")
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", (int) (get_row_cache()? get_row_cache()->get_limit() : 0));
GLOBAL_BINDING_END(get_row_cache_size)

GLOBAL_BINDING_START(set_board_cache_size, "set the size of the board cache")
  int count = 0;
  static char *keywords[] = { "max", NULL };
  if(!PyArg_ParseTupleAndKeywords(args, kwds, "i", keywords, &count)) return NULL;
  if (count < 0) return auto_exception(PyExc_ValueError, "value must be a positive integer");
  board_cache_limit = count;
  while (board_cache.size() > count) {
    board_cache.pop();
  }
  return Py_BuildValue("");
GLOBAL_BINDING_END(set_board_cache_size)

GLOBAL_BINDING_START(get_board_cache_size, "get the size of the board cache")
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", (int) board_cache_limit);
GLOBAL_BINDING_END(get_board_cache_size)


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
  static char *keywords[] = { "rows", NULL };
  if(!PyArg_ParseTupleAndKeywords(args, kwds, "|i", keywords, &count)) return -1;
  if (!self->obj) {
    self->obj = uncache_board(count);
    if (!self->obj) return auto_exception2(PyExc_RuntimeError, "could not allocate board");
  }
  if (count < 0 || count > 20) return auto_exception2(PyExc_ValueError, "invalid number of rows");
  self->obj->add_rows(count - (int) self->obj->pile_height());
  return 0;
}

static void python_tetris_20_10_dealloc_function(python_tetris_20_10 *self) {
  if (self->obj) {
    cache_board(self->obj);
    self->obj = NULL;
  }
}

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

METHOD_BINDING_START(tetris_20_10, mirror, "mirror another board")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  python_tetris_20_10 *other = NULL;
  if (!PyArg_ParseTuple(args, "O!", &python_tetris_20_10_type, &other)) return NULL;
  if (!other->obj) {
    other->obj = uncache_board();
    if (!other->obj) return auto_exception(PyExc_RuntimeError, "could not allocate board");
  }
  *self->obj = *other->obj;
  return Py_BuildValue("");
METHOD_BINDING_END(tetris_20_10, mirror)

METHOD_BINDING_START(tetris_20_10, uncow_all, "copy all copy-on-write rows")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  if (!PyArg_ParseTuple(args, "")) return NULL;
  self->obj->uncow_all();
  return Py_BuildValue("");
METHOD_BINDING_END(tetris_20_10, uncow_all)

METHOD_BINDING_START(tetris_20_10, row_count, "get the number of rows")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", (int) self->obj->row_count());
METHOD_BINDING_END(tetris_20_10, row_count)

METHOD_BINDING_START(tetris_20_10, col_count, "get the number of cols")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", (int) self->obj->col_count());
METHOD_BINDING_END(tetris_20_10, col_count)

METHOD_BINDING_START(tetris_20_10, pile_height, "get the pile height")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", (int) self->obj->pile_height());
METHOD_BINDING_END(tetris_20_10, pile_height)

METHOD_BINDING_START(tetris_20_10, add_rows, "add rows to the pile")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  int count = 0;
  static char *keywords[] = { "rows", NULL };
  if(!PyArg_ParseTupleAndKeywords(args, kwds, "i", keywords, &count)) return NULL;
  return Py_BuildValue("i", (int) self->obj->add_rows(count));
METHOD_BINDING_END(tetris_20_10, add_rows)

METHOD_BINDING_START(tetris_20_10, is_fake_row, "check if a row is faked")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  int r = 0;
  static char *keywords[] = { "r", NULL };
  if(!PyArg_ParseTupleAndKeywords(args, kwds, "i", keywords, &r)) return NULL;
  if (r < 0 || r >= (signed) self->obj->row_count()) return auto_exception(PyExc_IndexError, "index out of range");
  return use_object(self->obj->is_fake_row(r)? Py_True : Py_False);
METHOD_BINDING_END(tetris_20_10, is_fake_row)

METHOD_BINDING_START(tetris_20_10, is_mirrored_row, "check if a row is mirrored")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  int r = 0;
  static char *keywords[] = { "r", NULL };
  if(!PyArg_ParseTupleAndKeywords(args, kwds, "i", keywords, &r)) return NULL;
  if (r < 0 || r >= (signed) self->obj->row_count()) return auto_exception(PyExc_IndexError, "index out of range");
  return use_object(self->obj->is_mirrored_row(r)? Py_True : Py_False);
METHOD_BINDING_END(tetris_20_10, is_mirrored_row)

METHOD_BINDING_START(tetris_20_10, check_full, "check if any rows are full, optionally removing them")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  PyObject *clear = Py_False;
  static char *keywords[] = { "clear", NULL };
  if(!PyArg_ParseTupleAndKeywords(args, kwds, "|O", keywords, &clear)) return NULL;
  return Py_BuildValue("i", (int) self->obj->check_full(PyObject_IsTrue(clear)));
METHOD_BINDING_END(tetris_20_10, check_full)

METHOD_BINDING_START(tetris_20_10, check_empty, "check if any rows are empty, optionally removing them")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  PyObject *clear = Py_False;
  static char *keywords[] = { "clear", NULL };
  if(!PyArg_ParseTupleAndKeywords(args, kwds, "|O", keywords, &clear)) return NULL;
  return Py_BuildValue("i", (int) self->obj->check_empty(PyObject_IsTrue(clear)));
METHOD_BINDING_END(tetris_20_10, check_empty)

METHOD_BINDING_START(tetris_20_10, set_tamper_seal, "set the state of the tamper seal")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  PyObject *state = Py_True;
  static char *keywords[] = { "state", NULL };
  if(!PyArg_ParseTupleAndKeywords(args, kwds, "|O", keywords, &state)) return NULL;
  self->obj->set_tamper_seal(PyObject_IsTrue(state));
  return Py_BuildValue("");
METHOD_BINDING_END(tetris_20_10, set_tamper_seal)

METHOD_BINDING_START(tetris_20_10, get_tamper_seal, "get the state of the tamper seal")
  if (!self->obj) return auto_exception(PyExc_RuntimeError, "");
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return use_object(self->obj->get_tamper_seal()? Py_True : Py_False);
METHOD_BINDING_END(tetris_20_10, get_tamper_seal)


//list of all 'tetris_20_10' member functions

static PyMethodDef python_tetris_20_10_methods[] = {
  METHOD_BINDING(tetris_20_10, mirror),
  METHOD_BINDING(tetris_20_10, uncow_all),
  METHOD_BINDING(tetris_20_10, row_count),
  METHOD_BINDING(tetris_20_10, col_count),
  METHOD_BINDING(tetris_20_10, pile_height),
  METHOD_BINDING(tetris_20_10, add_rows),
  METHOD_BINDING(tetris_20_10, is_fake_row),
  METHOD_BINDING(tetris_20_10, is_mirrored_row),
  METHOD_BINDING(tetris_20_10, check_full),
  METHOD_BINDING(tetris_20_10, check_empty),
  METHOD_BINDING(tetris_20_10, set_tamper_seal),
  METHOD_BINDING(tetris_20_10, get_tamper_seal),
  NULL
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
  get_row_cache(DEFAULT_ROW_CACHE_SIZE);

  add_global_binding(&set_row_cache_size_binding);
  add_global_binding(&get_row_cache_size_binding);
  add_global_binding(&set_board_cache_size_binding);
  add_global_binding(&get_board_cache_size_binding);
}
