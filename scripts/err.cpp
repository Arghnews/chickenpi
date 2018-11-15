#include <iostream>
#include <new>
#include <exception>

int main (int /*argc*/, char** /*argv*/)
{
  //std::cout << "Hello world!" << "\n";
  //new int[2348423843249823];
  throw std::bad_alloc();
  return 1;
}
