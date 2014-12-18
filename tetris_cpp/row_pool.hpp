#ifndef row_pool_hpp
#define row_pool_hpp

#include <stack>
#include <memory>
#include <cassert>

#include "row_oper.hpp"


template <class Type>
class row_pool {
public:
  typedef Type                       row_type;
  typedef std::shared_ptr <row_type> row_pointer;
  typedef std::stack <row_pointer>   row_list;
  typedef row_oper <row_type>        row_ctrl;

  //size limit of pool, default element
  row_pool(size_t l, const row_type &d = row_type()) : limit(l), default_row() {
    ctrl.copy(d, default_row);
  }

private:
  row_pool(const row_pool&);
  row_pool &operator = (const row_pool&);

public:
  //get a new row from the pool
  row_pointer new_row() {
    return this->copy_row(default_row);
  }

  //get a new row from the pool, initializing it with the row passed as an argument
  row_pointer copy_row(const row_type &old_row) {
    if (!ctrl.validate(default_row, old_row)) return row_pointer();
    if (free_rows.size()) {
      row_pointer next = free_rows.top();
      free_rows.pop();
      assert(next.unique()); //(unique implies non-NULL)
      ctrl.copy(old_row, *next);
      return next;
    } else {
      return row_pointer(ctrl.new_copy(old_row));
    }
  }

  //set ownership of the row to this pool
  //NOTE: there must be exactly 1 reference to the row!
  //NOTE: if the row is accepted, the pointer is set to NULL
  bool reclaim_row(row_pointer &row) {
    if (free_rows.size() >= limit) return false;
    if (!row.unique()) return false;
    if (!ctrl.validate(default_row, *row)) return false;
    free_rows.push(row);
    row.reset();
    assert(free_rows.top().unique());
    return true;
  }

  //size limit of the pool
  size_t get_limit() const {
    return limit;
  }

  //number of free rows in the pool
  size_t get_count() const {
    return free_rows.size();
  }

  //set the size limit of the pool
  void set_limit(size_t l) {
    limit = l;
    while (this->get_count() > this->get_count()) free_rows.pop();
  }

  //get a reference to the default element
  row_type &get_default() {
    return default_row;
  }

  //get a reference to the default element
  const row_type &get_default() const {
    return default_row;
  }

  //set the default element to the argument
  bool set_default(const row_type &row) {
    if (!ctrl.validate(default_row, row)) return false;
    ctrl.copy(row, default_row);
    return true;
  }

private:
  size_t   limit;
  row_type default_row;
  row_ctrl ctrl;
  row_list free_rows;
};

#endif //row_pool_hpp
