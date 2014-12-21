#ifndef tetris_cow_hpp
#define tetris_cow_hpp

#include <memory>
#include <vector>
#include <cassert>
#include <string.h>

#include "abstract_board.hpp"
#include "row_pool.hpp"


//dynamically-sized board

template <class Type>
class tetris_cow_storage : public abstract_board <Type> {
public:
  using typename abstract_board <Type>                ::cell_type;
  typedef std::vector <cell_type>                       row_type;
  typedef row_pool <row_type>                           row_cache;
  typedef std::shared_ptr <row_cache>                   row_cache_pointer;
  typedef std::vector <typename row_cache::row_pointer> board_rows;

  //cache of rows to use, number of initial rows
  tetris_cow_storage(const row_cache_pointer &p = row_cache_pointer(),
    size_t r = 0, size_t c = 0) :
  rows(r), cols(c), used_rows(0), cache(p), board(r) {}

  void clear_all() {}

  tetris_cow_storage &operator = (const tetris_cow_storage &other) {
    if (&other == this) return *this;
    this->clear_all();
    rows      = other.rows;
    cols      = other.cols;
    used_rows = other.used_rows;
    cache     = other.cache;
    for (size_t r = 0; r < rows; r++) {
      board[r] = other.board[r];
    }
    return *this;
  }

  //get the number of rows
  size_t row_count() const {
    return rows;
  }

  //get the number of cols
  size_t col_count() const {
    return cols;
  }

  //get the number of rows in the pile
  size_t pile_height() const {
    return used_rows;
  }

protected:
  size_t            rows, cols; //NOTE: not 'const' so assignment will work!
  size_t            used_rows;
  row_cache_pointer cache;
  board_rows        board;
};


//statically-sized board

template <class Type, size_t Rows, size_t Cols>
class tetris_cow_storage <Type[Rows][Cols]> : public abstract_board <Type> {
public:
  using typename abstract_board <Type>  ::cell_type;
  typedef cell_type                       row_type[Cols];
  typedef row_pool <row_type>             row_cache;
  typedef std::shared_ptr <row_cache>     row_cache_pointer;
  typedef typename row_cache::row_pointer board_rows[Rows];

  //cache of rows to use, number of initial rows
  tetris_cow_storage(const row_cache_pointer &p = row_cache_pointer()) : used_rows(0), cache(p) {}

  void clear_all() {}

  tetris_cow_storage &operator = (const tetris_cow_storage &other) {
    if (&other == this) return *this;
    this->clear_all();
    used_rows = other.used_rows;
    cache     = other.cache;
    for (size_t r = 0; r < Rows; r++) {
      board[r] = other.board[r];
    }
    return *this;
  }

private:
  tetris_cow_storage(const tetris_cow_storage&) {}

public:
  //get the number of rows
  size_t row_count() const {
    return Rows;
  }

  //get the number of cols
  size_t col_count() const {
    return Cols;
  }

  //get the number of rows in the pile
  size_t pile_height() const {
    return used_rows;
  }

protected:
  size_t            used_rows;
  row_cache_pointer cache;
  board_rows        board;
};


template <class Type>
class tetris_cow_logic : virtual public tetris_cow_storage <Type> {
public:
  using typename tetris_cow_storage <Type> ::cell_type;
  using typename tetris_cow_storage <Type> ::row_type;
  using tetris_cow_storage <Type> ::used_rows;
  using tetris_cow_storage <Type> ::cache;
  using tetris_cow_storage <Type> ::board;

  tetris_cow_logic() : tamper(false) {}

  //clear all rows of the board
  void clear_all() {
    for (size_t r = 0; r < this->row_count(); r++) {
      if (cache && cache->reclaim_row(board[r])) /*nothing*/;
      else board[r].reset();
    }
    this->set_tamper_seal(false);
    used_rows = 0;
  }

  //get a cell value
  //NOTE: this isn't a reference, in case the cell value needs to be faked
  cell_type get_cell(size_t r, size_t c) const {
    assert(r >= 0 && r < this->row_count());
    assert(c >= 0 && c < this->col_count());
    if (!board[r]) return cell_type();
    return (*board[r])[c];
  }

  //set a cell value
  //NOTE: this is copy-on-write if there are other references to the row being written to
  const cell_type &set_cell(size_t r, size_t c, const cell_type &val) {
    assert(r >= 0 && r < this->pile_height());
    assert(c >= 0 && c < this->col_count());
    if (!board[r].unique()) {
      assert(cache.get());
      board[r] = cache->copy_row(*board[r]);
    }
    assert(board[r].get());
    this->set_tamper_seal(false);
    return (*board[r])[c] = val;
  }

  //copy all copy-on-write rows
  void uncow_all() {
    if (this->pile_height()) assert(cache.get());
    for (size_t r = 0; r < this->pile_height(); r++) {
      board[r] = cache->copy_row(*board[r]);
    }
  }

  //add one or more default rows
  //NOTE: the argument is signed so that negative values can be passsed!
  size_t add_rows(ssize_t rows) {
    if (rows > 0) assert(cache.get());
    size_t added = 0;
    for (; rows > 0 && used_rows < this->row_count(); added++, rows--) {
      assert(!board[used_rows]);
      board[used_rows++] = cache->new_row();
    }
    if (added) this->set_tamper_seal(false);
    return added;
  }

  //set a row to the argument passed
  //NOTE: this expands the board from the bottom until the row being written to exists
  void set_row(size_t r, const row_type &row) {
    assert(r >= 0 && r < this->row_count());
    if (r >= used_rows) this->add_rows(r - used_rows + 1);
    //NOTE: use 'set_cell' so that copy-on-write is respected
    for (size_t c = 0; c < this->col_count(); c++) this->set_cell(r, c, row[c]);
    this->set_tamper_seal(false);
  }

  //check if a row is fake, i.e., is NULL
  bool is_fake_row(size_t r) const {
    assert(r >= 0 && r < this->row_count());
    return !board[r];
  }

  //check if a row is referenced by another board
  bool is_mirrored_row(size_t r) const {
    assert(r >= 0 && r < this->row_count());
    return board[r] && !board[r].unique();
  }

  //check for full rows; to delete them, pass 'true'
  size_t check_full(bool clear = false) {
    return check_all_rows(true, clear);
  }

  //check for empty rows; to delete them, pass 'true'
  size_t check_empty(bool clear = false) {
    return check_all_rows(false, clear);
  }

  void set_tamper_seal(bool t) {
    tamper = t;
  }

  bool get_tamper_seal() const {
    return tamper;
  }

  ~tetris_cow_logic() {
    this->clear_all();
  }

private:
  //check, and optionally delete, a full/empty row
  bool check_row(size_t r, bool full, bool clear) {
    if (board[r]) {
      for (size_t c = 0; c < this->col_count(); c++) {
        if ((bool) this->get_cell(r, c) ^ full) return false;
      }
    }
    if (clear) {
      assert(cache.get());
      //NOTE: 'cache.reclaim_row' has no effect if the row isn't unique
      if (!cache->reclaim_row(board[r])) board[r].reset();
      this->set_tamper_seal(false);
    }
    return true;
  }

  //check, and optionally delete, all full/empty rows
  size_t check_all_rows(bool full, bool clear) {
    size_t count = 0;
    for (size_t r = 0; r < this->pile_height(); r++) {
      if (this->check_row(r, full, clear)) count++;
    }
    if (clear && count) this->drop_rows();
    return count;
  }

  //drop NULL rows from the board and adjust its effective size
  void drop_rows() {
    size_t out = 0;
    //move all non-NULL rows down
    for (size_t in = 0; in < this->pile_height(); in++) {
      if (board[in]) {
        if (in != out) board[out] = board[in];
        out++;
      }
    }
    //NULL out everything above the top row
    //NOTE: don't use 'cache.reclaim_row' because these rows are still in use!
    for (size_t in = out; in < this->pile_height(); in++) board[in].reset();
    used_rows = out;
    this->set_tamper_seal(false);
  }

  bool tamper;
};


//dynamically-sized board

template <class Type>
struct tetris_cow : virtual public tetris_cow_storage <Type>, public tetris_cow_logic <Type> {
  using typename tetris_cow_storage <Type> ::row_cache_pointer;
  using tetris_cow_storage <Type> ::used_rows;
  using tetris_cow_storage <Type> ::cache;
  using tetris_cow_storage <Type> ::board;

  tetris_cow(const row_cache_pointer &p, size_t r, size_t c, size_t r2 = 0) :
  tetris_cow_storage <Type> (p, r, c) {
    this->add_rows(r2);
  }
};


//statically-sized board

template <class Type, size_t Rows, size_t Cols>
struct tetris_cow <Type[Rows][Cols]> : virtual public tetris_cow_storage <Type[Rows][Cols]>, public tetris_cow_logic <Type[Rows][Cols]> {
  using typename tetris_cow_storage <Type[Rows][Cols]> ::row_cache_pointer;
  using tetris_cow_storage <Type[Rows][Cols]> ::used_rows;
  using tetris_cow_storage <Type[Rows][Cols]> ::cache;
  using tetris_cow_storage <Type[Rows][Cols]> ::board;

  tetris_cow(const row_cache_pointer &p, size_t r = 0) :
  tetris_cow_storage <Type[Rows][Cols]> (p) {
    this->add_rows(r);
  }
};

#endif //tetris_cow_hpp
