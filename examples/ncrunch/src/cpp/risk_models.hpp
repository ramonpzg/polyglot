#pragma once

#include <algorithm>
#include <ranges>
#include <vector>

namespace numcrunch::risk {

template <class Range>
auto percentile(Range&& r, double p) {
  using std::ranges::begin;
  using std::ranges::end;
  std::vector<typename std::ranges::range_value_t<Range>> v(begin(r), end(r));
  std::ranges::sort(v);
  auto pos = static_cast<std::size_t>(p * (v.size() - 1));
  return v[pos];
}

}  // namespace numcrunch::risk

