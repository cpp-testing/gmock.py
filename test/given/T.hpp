namespace n {

template <typename Elem>
class T {
  virtual ~T();

  virtual int GetSize() const = 0;
  virtual void Push(const Elem& x) = 0;
};

} // namespace n

