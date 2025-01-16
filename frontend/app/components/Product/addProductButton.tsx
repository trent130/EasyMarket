import { Plus } from "lucide-react";
import { AddProductModal } from "./addProductModal";
import { useState } from "react";
export const AddProductButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="group inline-flex items-center gap-2 bg-black text-white px-4 py-2 rounded-lg transition-all duration-200 hover:bg-gray-900 active:scale-95"
      >
        <Plus className="w-5 h-5 transition-transform group-hover:rotate-90" />
        <span className="font-medium">Add Product</span>
      </button>
      <AddProductModal open={isOpen} onOpenChange={setIsOpen} />
    </>
  );
};