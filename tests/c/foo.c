int main{
  #ifdef FOO
    func();
  #endif
  #ifdef BAR
    func2();
  #endif
}

