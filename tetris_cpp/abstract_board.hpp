#ifndef abstract_board_hpp
#define abstract_board_hpp

#include <cstring> //(for 'ssize_t')


template <class Type>
class abstract_board {
public:
  typedef Type cell_type;

  virtual void clear_all() = 0;

  virtual cell_type get_cell(size_t r, size_t c) const = 0;

  virtual const cell_type &set_cell(size_t r, size_t c, const cell_type &val) = 0;

  virtual void uncow_all() = 0;

  virtual size_t row_count() const = 0;

  virtual size_t col_count() const = 0;

  virtual size_t pile_height() const = 0;

  virtual size_t add_rows(ssize_t rows) = 0;

  virtual bool is_fake_row(size_t r) const = 0;

  virtual bool is_mirrored_row(size_t r) const = 0;

  virtual size_t check_full(bool clear = false) = 0;

  virtual size_t check_empty(bool clear = false) = 0;

  virtual void set_tamper_seal(bool) = 0;

  virtual bool get_tamper_seal() const = 0;

  virtual inline ~abstract_board() {}
};

#endif //abstract_board_hpp
