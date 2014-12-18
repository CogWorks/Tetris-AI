#ifndef row_oper_hpp
#define row_oper_hpp


//row operations, specialized for the different possible row types
template <class> struct row_oper;


//row operations for containers
template <class Type>
struct row_oper_iter {
  virtual void reset(Type &row) {
    for (typename Type::iterator current = row.begin(), end = row.end();
      current != end; ++current)
    *current = typename Type::value_type();
  }

  virtual bool validate(const Type &ref, const Type &row) {
    return row.size() == ref.size();
  }

  virtual void copy(const Type &old_row, Type &new_row) {
    new_row = old_row;
  }

  virtual Type *new_copy(const Type &old_row) {
    return new Type(old_row);
  }
};


#define ROW_OPER_ITER(type) \
template <class Type> struct row_oper <type <Type> > : public row_oper_iter <type <Type> > {};

#include <vector>
ROW_OPER_ITER(std::vector)

#include <list>
ROW_OPER_ITER(std::list)

#include <valarray>
ROW_OPER_ITER(std::valarray)

#include <deque>
ROW_OPER_ITER(std::deque)

#undef ROW_OPER_ITER


//row operations for arrays
template <class Type, size_t Size>
struct row_oper_array {
  typedef Type(type)[Size];

  virtual void reset(type &row) {
    for (size_t i = 0; i < Size; i++)
    row[i] = Type();
  }

  virtual bool validate(const type &row, const type &ref) {
    return true;
  }

  virtual void copy(const type &old_row, type &new_row) {
    for (size_t i = 0; i < Size; i++)
    new_row[i] = old_row[i];
  }

  virtual type *new_copy(const type &old_row) {
    type *new_row = reinterpret_cast <type*> (new Type[Size]);
    assert(new_row);
    this->copy(old_row, *new_row);
    return new_row;
  }
};


template <class Type, size_t Size>
struct row_oper <Type[Size]> : public row_oper_array <Type, Size> {};


//row operations for integer arrays
template <class Type, size_t Size>
struct row_oper_int : public row_oper_array <Type, Size> {
  using typename row_oper_array <Type, Size> ::type;

  void reset(type &row) {
    memset(row, 0, sizeof row);
  }

  void copy(const type &old_row, type &new_row) {
    memcpy(new_row, old_row, sizeof old_row);
  }
};


#define ROW_OPER_INT(type) \
template <size_t Size> struct row_oper <type[Size]> : public row_oper_int <type, Size> {};

ROW_OPER_INT(int)
ROW_OPER_INT(unsigned int)
ROW_OPER_INT(long)
ROW_OPER_INT(unsigned long)
ROW_OPER_INT(short)
ROW_OPER_INT(unsigned short)
ROW_OPER_INT(char)
ROW_OPER_INT(unsigned char)

#undef ROW_OPER_INT

#endif //row_oper_hpp
